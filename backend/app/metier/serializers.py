"""Serializers pour l'application metier (remise à neuf)."""
from rest_framework import serializers
from app.metier.models import Dragon, Elitest, Elitesty, Fusion

# Ajoutez vos serializers personnalisés ici.


from app.metier.services.storage_service import get_storage_service
class ElitestSerializer(serializers.ModelSerializer):
    """
    Serializer pour les elitests.
    """
    
    class Meta:
        model = Elitest
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'uuid', 'titre', 'statut', 'description', 'prix', 'document', 'created_by', 'updated_by', 'created_at', 'updated_at', 'elitesties']
        depth = 1

    def get_fields(self):
        """
        Marque les champs système en lecture seule s'ils existent.
        """
        fields = super().get_fields()
        for sys_field in ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def to_representation(self, instance):
        """
        Personnalise la représentation des données.
        """
        data = super().to_representation(instance)
        
        data['created_at'] = instance.created_at.isoformat() if hasattr(instance, 'created_at') else None
        data['updated_at'] = instance.updated_at.isoformat() if hasattr(instance, 'updated_at') else None
        storage = get_storage_service()
        if getattr(instance, 'document', None):
            data['document_url'] = storage.url(getattr(instance, 'document'))
        
        
        # Ajouter les données de la relation elitesties si elle existe
        if hasattr(instance, 'elitesties'):
            elitesties_data = []
            for item in instance.elitesties.all():
                elitesties_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['elitesties'] = elitesties_data
        else:
            data['elitesties'] = []
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class ElitestySerializer(serializers.ModelSerializer):
    """
    Serializer pour les elitesties.
    """
    
    class Meta:
        model = Elitesty
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'uuid', 'titre', 'statut', 'description', 'prix', 'document', 'created_by', 'updated_by', 'created_at', 'updated_at']
        depth = 1

    def get_fields(self):
        """
        Marque les champs système en lecture seule s'ils existent.
        """
        fields = super().get_fields()
        for sys_field in ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def to_representation(self, instance):
        """
        Personnalise la représentation des données.
        """
        data = super().to_representation(instance)
        
        data['created_at'] = instance.created_at.isoformat() if hasattr(instance, 'created_at') else None
        data['updated_at'] = instance.updated_at.isoformat() if hasattr(instance, 'updated_at') else None
        storage = get_storage_service()
        if getattr(instance, 'document', None):
            data['document_url'] = storage.url(getattr(instance, 'document'))
        
        
        # Ajouter les données des relations elitests (reverse FK)
        if hasattr(instance, 'elitests'):
            elitests_data = []
            for item in instance.elitests.all():
                elitests_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['elitests'] = elitests_data
        else:
            data['elitests'] = []
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class DragonSerializer(serializers.ModelSerializer):
    """
    Serializer pour les dragons.
    """
    
    class Meta:
        model = Dragon
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'uuid', 'titre', 'statut', 'description', 'prix', 'document', 'created_by', 'updated_by', 'created_at', 'updated_at', 'fusion']

    def create(self, validated_data):
        """
        Crée une nouvelle instance de Dragon.
        """
        # Conversion automatique fusion ID vers objet
        if 'fusion' in validated_data and not isinstance(validated_data['fusion'], Fusion):
            try:
                pk = int(validated_data['fusion'])  # gère str ou int
                fusion_obj = Fusion.objects.get(pk=pk)
                validated_data['fusion'] = fusion_obj
            except (ValueError, Fusion.DoesNotExist):
                raise serializers.ValidationError({'fusion': 'Fusion avec cet ID n\'existe pas.'})
        
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Met à jour une instance de Dragon.
        """
        # Conversion automatique fusion ID vers objet
        if 'fusion' in validated_data and not isinstance(validated_data['fusion'], Fusion):
            try:
                pk = int(validated_data['fusion'])  # gère str ou int
                fusion_obj = Fusion.objects.get(pk=pk)
                validated_data['fusion'] = fusion_obj
            except (ValueError, Fusion.DoesNotExist):
                raise serializers.ValidationError({'fusion': 'Fusion avec cet ID n\'existe pas.'})
        
        
        return super().update(instance, validated_data)
        
        
        depth = 1

    def get_fields(self):
        """
        Marque les champs système en lecture seule s'ils existent.
        """
        fields = super().get_fields()
        for sys_field in ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def to_representation(self, instance):
        """
        Personnalise la représentation des données.
        """
        data = super().to_representation(instance)
        
        data['created_at'] = instance.created_at.isoformat() if hasattr(instance, 'created_at') else None
        data['updated_at'] = instance.updated_at.isoformat() if hasattr(instance, 'updated_at') else None
        storage = get_storage_service()
        if getattr(instance, 'document', None):
            data['document_url'] = storage.url(getattr(instance, 'document'))
        
        
        # Ajouter les données de la relation fusion si elle existe
        if hasattr(instance, 'fusion') and instance.fusion:
            data['fusion'] = {
                'id': instance.fusion.id,
                '__str__': str(instance.fusion),
            }
        else:
            data['fusion'] = None
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class FusionSerializer(serializers.ModelSerializer):
    """
    Serializer pour les fusions.
    """
    
    class Meta:
        model = Fusion
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'uuid', 'titre', 'statut', 'description', 'prix', 'document', 'created_by', 'updated_by', 'created_at', 'updated_at']
        depth = 1

    def get_fields(self):
        """
        Marque les champs système en lecture seule s'ils existent.
        """
        fields = super().get_fields()
        for sys_field in ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def to_representation(self, instance):
        """
        Personnalise la représentation des données.
        """
        data = super().to_representation(instance)
        
        data['created_at'] = instance.created_at.isoformat() if hasattr(instance, 'created_at') else None
        data['updated_at'] = instance.updated_at.isoformat() if hasattr(instance, 'updated_at') else None
        storage = get_storage_service()
        if getattr(instance, 'document', None):
            data['document_url'] = storage.url(getattr(instance, 'document'))
        
        
        # Ajouter les données des relations dragons (reverse FK)
        if hasattr(instance, 'dragons'):
            dragons_data = []
            for item in instance.dragons.all():
                dragons_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['dragons'] = dragons_data
        else:
            data['dragons'] = []
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data
