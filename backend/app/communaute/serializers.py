from rest_framework import serializers
from app.communaute.models import AvisChoix, Commentaire, ConfirmationAide, Conversation, Espace, ImagePublication, LienInvitation, LikeCommentaire, LikePublication, Message, NotificationResume, OptionPublication, ParticipationEspace, Publication, SuiviUtilisateur, VoteSondage


class AvisChoixSerializer(serializers.ModelSerializer):
    """
    Serializer pour les avis-choix.
    """
    
    class Meta:
        model = AvisChoix
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'explication', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class CommentaireSerializer(serializers.ModelSerializer):
    """
    Serializer pour les commentaires.
    """
    
    class Meta:
        model = Commentaire
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'nature', 'texte', 'est_anonyme', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class ConfirmationAideSerializer(serializers.ModelSerializer):
    """
    Serializer pour les confirmations-aide.
    """
    
    class Meta:
        model = ConfirmationAide
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les conversations.
    """
    
    class Meta:
        model = Conversation
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class EspaceSerializer(serializers.ModelSerializer):
    """
    Serializer pour les espaces.
    """
    
    class Meta:
        model = Espace
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'type', 'nom', 'description', 'acces', 'membres_peuvent_publier', 'commentaires_ouverts', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class ImagePublicationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les images-publication.
    """
    
    class Meta:
        model = ImagePublication
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'url', 'texte_alternatif', 'position', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class LienInvitationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les liens-invitation.
    """
    
    class Meta:
        model = LienInvitation
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'code_hash', 'previsualisation_autorisee', 'revoked_at', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class LikeCommentaireSerializer(serializers.ModelSerializer):
    """
    Serializer pour les likes-commentaire.
    """
    
    class Meta:
        model = LikeCommentaire
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class LikePublicationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les likes-publication.
    """
    
    class Meta:
        model = LikePublication
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer pour les messages.
    """
    
    class Meta:
        model = Message
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'texte', 'sent_at', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class NotificationResumeSerializer(serializers.ModelSerializer):
    """
    Serializer pour les notifications-resume.
    """
    
    class Meta:
        model = NotificationResume
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'periode_debut', 'periode_fin', 'nombre_nouveautes', 'read_at', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class OptionPublicationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les options-publication.
    """
    
    class Meta:
        model = OptionPublication
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'libelle', 'description', 'image_url', 'position', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class ParticipationEspaceSerializer(serializers.ModelSerializer):
    """
    Serializer pour les participations-espace.
    """
    
    class Meta:
        model = ParticipationEspace
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'role', 'joined_at', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class PublicationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les publications.
    """
    
    class Meta:
        model = Publication
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'type', 'titre', 'description', 'lien_app', 'plateforme_app', 'contraintes', 'justification_finale', 'decided_at', 'mode_vote', 'votes_fermes_at', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class SuiviUtilisateurSerializer(serializers.ModelSerializer):
    """
    Serializer pour les suivis-utilisateur.
    """
    
    class Meta:
        model = SuiviUtilisateur
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class VoteSondageSerializer(serializers.ModelSerializer):
    """
    Serializer pour les votes-sondage.
    """
    
    class Meta:
        model = VoteSondage
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']

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
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data
