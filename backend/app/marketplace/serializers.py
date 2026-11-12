from rest_framework import serializers
from app.marketplace.models import Availability, Candidature, Company, Connection, Experience, Offer, Prestation, Profil, ProfilHistory, ProfilSkill, Review, Skill, Swipe
from app.metier.services.storage_service import get_storage_service


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer pour les companies.
    """
    
    class Meta:
        model = Company
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'name', 'slug', 'logo', 'description', 'sector', 'size', 'website', 'contact_email', 'phone', 'country', 'city', 'address', 'is_verified', 'verified_at', 'created_by', 'updated_by', 'created_at', 'updated_at']
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
        if getattr(instance, 'logo', None):
            data['logo_url'] = storage.url(getattr(instance, 'logo'))
        
        
        # Ajouter les données des relations profils (reverse FK)
        if hasattr(instance, 'profils'):
            profils_data = []
            for item in instance.profils.all():
                profils_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['profils'] = profils_data
        else:
            data['profils'] = []
        
        
        # Ajouter les données des relations offers (reverse FK)
        if hasattr(instance, 'offers'):
            offers_data = []
            for item in instance.offers.all():
                offers_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['offers'] = offers_data
        else:
            data['offers'] = []
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer pour les skills.
    """
    
    class Meta:
        model = Skill
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'name', 'slug', 'type', 'category', 'created_by', 'updated_by', 'created_at', 'updated_at']
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
        
        
        # Ajouter les données des relations offers (reverse FK)
        if hasattr(instance, 'offers'):
            offers_data = []
            for item in instance.offers.all():
                offers_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['offers'] = offers_data
        else:
            data['offers'] = []
        
        
        # Ajouter les données des relations profil_skills (reverse FK)
        if hasattr(instance, 'profil_skills'):
            profil_skills_data = []
            for item in instance.profil_skills.all():
                profil_skills_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['profil_skills'] = profil_skills_data
        else:
            data['profil_skills'] = []
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class ProfilSerializer(serializers.ModelSerializer):
    """
    Serializer pour les profils.
    """
    
    # Compte lié : identifiant seul (un depth=1 exposerait l'utilisateur complet)
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Profil
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'user_id', 'is_company_owner', 'slug', 'photo', 'headline', 'bio', 'phone', 'country', 'city', 'remote', 'timezone', 'default_hours_per_week', 'is_open_to_work', 'daily_rate', 'currency', 'years_of_experience', 'languages', 'github_url', 'linkedin_url', 'portfolio_url', 'cv_visibility', 'embedding', 'created_by', 'updated_by', 'created_at', 'updated_at', 'company']
        depth = 1

    def _resolve_relations(self, validated_data):
        """Convertit les identifiants de clés étrangères en instances (message d'erreur par champ)."""
        for field, model_cls in (('company', Company),):
            value = validated_data.get(field)
            if value is not None and not isinstance(value, model_cls):
                try:
                    validated_data[field] = model_cls.objects.get(pk=int(value))
                except (ValueError, TypeError, model_cls.DoesNotExist):
                    raise serializers.ValidationError({field: f"{model_cls.__name__} avec cet ID n'existe pas."})
        return validated_data

    def create(self, validated_data):
        """
        Crée une nouvelle instance de Profil.
        """
        return super().create(self._resolve_relations(validated_data))

    def update(self, instance, validated_data):
        """
        Met à jour une instance de Profil.
        """
        return super().update(instance, self._resolve_relations(validated_data))

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
        if getattr(instance, 'photo', None):
            data['photo_url'] = storage.url(getattr(instance, 'photo'))
        
        
        # Ajouter les données de la relation company si elle existe
        if hasattr(instance, 'company') and instance.company:
            data['company'] = {
                'id': instance.company.id,
                '__str__': str(instance.company),
            }
        else:
            data['company'] = None
        
        
        # Ajouter les données des relations created_offers (reverse FK)
        if hasattr(instance, 'created_offers'):
            created_offers_data = []
            for item in instance.created_offers.all():
                created_offers_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['created_offers'] = created_offers_data
        else:
            data['created_offers'] = []
        
        
        # Ajouter les données des relations candidatures (reverse FK)
        if hasattr(instance, 'candidatures'):
            candidatures_data = []
            for item in instance.candidatures.all():
                candidatures_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['candidatures'] = candidatures_data
        else:
            data['candidatures'] = []
        
        
        # Ajouter les données des relations profil_skills (reverse FK)
        if hasattr(instance, 'profil_skills'):
            profil_skills_data = []
            for item in instance.profil_skills.all():
                profil_skills_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['profil_skills'] = profil_skills_data
        else:
            data['profil_skills'] = []
        
        
        # Ajouter les données des relations experiences (reverse FK)
        if hasattr(instance, 'experiences'):
            experiences_data = []
            for item in instance.experiences.all():
                experiences_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['experiences'] = experiences_data
        else:
            data['experiences'] = []
        
        
        # Ajouter les données des relations prestations (reverse FK)
        if hasattr(instance, 'prestations'):
            prestations_data = []
            for item in instance.prestations.all():
                prestations_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['prestations'] = prestations_data
        else:
            data['prestations'] = []
        
        
        # Ajouter les données des relations history (reverse FK)
        if hasattr(instance, 'history'):
            history_data = []
            for item in instance.history.all():
                history_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['history'] = history_data
        else:
            data['history'] = []
        
        
        # Ajouter les données des relations availabilities (reverse FK)
        if hasattr(instance, 'availabilities'):
            availabilities_data = []
            for item in instance.availabilities.all():
                availabilities_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['availabilities'] = availabilities_data
        else:
            data['availabilities'] = []
        
        
        # Ajouter les données des relations reviews_received (reverse FK)
        if hasattr(instance, 'reviews_received'):
            reviews_received_data = []
            for item in instance.reviews_received.all():
                reviews_received_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['reviews_received'] = reviews_received_data
        else:
            data['reviews_received'] = []
        
        
        # Ajouter les données des relations reviews_given (reverse FK)
        if hasattr(instance, 'reviews_given'):
            reviews_given_data = []
            for item in instance.reviews_given.all():
                reviews_given_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['reviews_given'] = reviews_given_data
        else:
            data['reviews_given'] = []
        
        
        # Ajouter les données des relations swipes_given (reverse FK)
        if hasattr(instance, 'swipes_given'):
            swipes_given_data = []
            for item in instance.swipes_given.all():
                swipes_given_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['swipes_given'] = swipes_given_data
        else:
            data['swipes_given'] = []
        
        
        # Ajouter les données des relations swipes_received (reverse FK)
        if hasattr(instance, 'swipes_received'):
            swipes_received_data = []
            for item in instance.swipes_received.all():
                swipes_received_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['swipes_received'] = swipes_received_data
        else:
            data['swipes_received'] = []
        
        
        # Ajouter les données des relations connections_as_a (reverse FK)
        if hasattr(instance, 'connections_as_a'):
            connections_as_a_data = []
            for item in instance.connections_as_a.all():
                connections_as_a_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['connections_as_a'] = connections_as_a_data
        else:
            data['connections_as_a'] = []
        
        
        # Ajouter les données des relations connections_as_b (reverse FK)
        if hasattr(instance, 'connections_as_b'):
            connections_as_b_data = []
            for item in instance.connections_as_b.all():
                connections_as_b_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['connections_as_b'] = connections_as_b_data
        else:
            data['connections_as_b'] = []
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer pour les offers.
    """
    
    class Meta:
        model = Offer
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'title', 'slug', 'description', 'type', 'contract_duration', 'experience_level', 'budget_min', 'budget_max', 'currency', 'budget_period', 'country', 'city', 'work_mode', 'start_date', 'deadline', 'status', 'published_at', 'views_count', 'embedding', 'created_by', 'updated_by', 'created_at', 'updated_at', 'company', 'recruiter', 'required_skills']
        depth = 1

    def _resolve_relations(self, validated_data):
        """Convertit les identifiants de clés étrangères en instances (message d'erreur par champ)."""
        for field, model_cls in (('company', Company), ('recruiter', Profil),):
            value = validated_data.get(field)
            if value is not None and not isinstance(value, model_cls):
                try:
                    validated_data[field] = model_cls.objects.get(pk=int(value))
                except (ValueError, TypeError, model_cls.DoesNotExist):
                    raise serializers.ValidationError({field: f"{model_cls.__name__} avec cet ID n'existe pas."})
        return validated_data

    def create(self, validated_data):
        """
        Crée une nouvelle instance de Offer.
        """
        return super().create(self._resolve_relations(validated_data))

    def update(self, instance, validated_data):
        """
        Met à jour une instance de Offer.
        """
        return super().update(instance, self._resolve_relations(validated_data))

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
        
        
        # Ajouter les données de la relation company si elle existe
        if hasattr(instance, 'company') and instance.company:
            data['company'] = {
                'id': instance.company.id,
                '__str__': str(instance.company),
            }
        else:
            data['company'] = None
        
        
        # Ajouter les données de la relation recruiter si elle existe
        if hasattr(instance, 'recruiter') and instance.recruiter:
            data['recruiter'] = {
                'id': instance.recruiter.id,
                '__str__': str(instance.recruiter),
            }
        else:
            data['recruiter'] = None
        
        
        # Ajouter les données de la relation required_skills si elle existe
        if hasattr(instance, 'required_skills'):
            required_skills_data = []
            for item in instance.required_skills.all():
                required_skills_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['required_skills'] = required_skills_data
        else:
            data['required_skills'] = []
        
        
        # Ajouter les données des relations candidatures (reverse FK)
        if hasattr(instance, 'candidatures'):
            candidatures_data = []
            for item in instance.candidatures.all():
                candidatures_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['candidatures'] = candidatures_data
        else:
            data['candidatures'] = []
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class CandidatureSerializer(serializers.ModelSerializer):
    """
    Serializer pour les candidatures.
    """
    
    class Meta:
        model = Candidature
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'message', 'status', 'ai_match_score', 'cv_snapshot', 'decided_at', 'created_by', 'updated_by', 'created_at', 'updated_at', 'offer', 'profil']
        depth = 1

    def _resolve_relations(self, validated_data):
        """Convertit les identifiants de clés étrangères en instances (message d'erreur par champ)."""
        for field, model_cls in (('profil', Profil), ('offer', Offer),):
            value = validated_data.get(field)
            if value is not None and not isinstance(value, model_cls):
                try:
                    validated_data[field] = model_cls.objects.get(pk=int(value))
                except (ValueError, TypeError, model_cls.DoesNotExist):
                    raise serializers.ValidationError({field: f"{model_cls.__name__} avec cet ID n'existe pas."})
        return validated_data

    def create(self, validated_data):
        """
        Crée une nouvelle instance de Candidature.
        """
        return super().create(self._resolve_relations(validated_data))

    def update(self, instance, validated_data):
        """
        Met à jour une instance de Candidature.
        """
        return super().update(instance, self._resolve_relations(validated_data))

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
        if getattr(instance, 'cv_snapshot', None):
            data['cv_snapshot_url'] = storage.url(getattr(instance, 'cv_snapshot'))
        
        
        # Ajouter les données de la relation offer si elle existe
        if hasattr(instance, 'offer') and instance.offer:
            data['offer'] = {
                'id': instance.offer.id,
                '__str__': str(instance.offer),
            }
        else:
            data['offer'] = None
        
        
        # Ajouter les données de la relation profil si elle existe
        if hasattr(instance, 'profil') and instance.profil:
            data['profil'] = {
                'id': instance.profil.id,
                '__str__': str(instance.profil),
            }
        else:
            data['profil'] = None
        
        
        # Ajouter les données des relations reviews (reverse FK)
        if hasattr(instance, 'reviews'):
            reviews_data = []
            for item in instance.reviews.all():
                reviews_data.append({
                    'id': item.id,
                    '__str__': str(item),
                })
            data['reviews'] = reviews_data
        else:
            data['reviews'] = []
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class ProfilSkillSerializer(serializers.ModelSerializer):
    """
    Serializer pour les profil-skills.
    """
    
    class Meta:
        model = ProfilSkill
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'level', 'years', 'created_by', 'updated_by', 'created_at', 'updated_at', 'profil', 'skill']
        depth = 1

    def _resolve_relations(self, validated_data):
        """Convertit les identifiants de clés étrangères en instances (message d'erreur par champ)."""
        for field, model_cls in (('profil', Profil), ('skill', Skill),):
            value = validated_data.get(field)
            if value is not None and not isinstance(value, model_cls):
                try:
                    validated_data[field] = model_cls.objects.get(pk=int(value))
                except (ValueError, TypeError, model_cls.DoesNotExist):
                    raise serializers.ValidationError({field: f"{model_cls.__name__} avec cet ID n'existe pas."})
        return validated_data

    def create(self, validated_data):
        """
        Crée une nouvelle instance de ProfilSkill.
        """
        return super().create(self._resolve_relations(validated_data))

    def update(self, instance, validated_data):
        """
        Met à jour une instance de ProfilSkill.
        """
        return super().update(instance, self._resolve_relations(validated_data))

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
        
        
        # Ajouter les données de la relation profil si elle existe
        if hasattr(instance, 'profil') and instance.profil:
            data['profil'] = {
                'id': instance.profil.id,
                '__str__': str(instance.profil),
            }
        else:
            data['profil'] = None
        
        
        # Ajouter les données de la relation skill si elle existe
        if hasattr(instance, 'skill') and instance.skill:
            data['skill'] = {
                'id': instance.skill.id,
                '__str__': str(instance.skill),
            }
        else:
            data['skill'] = None
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class ExperienceSerializer(serializers.ModelSerializer):
    """
    Serializer pour les experiences.
    """
    
    class Meta:
        model = Experience
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'title', 'company_name', 'location', 'contract_type', 'start_date', 'end_date', 'is_current', 'description', 'technologies', 'created_by', 'updated_by', 'created_at', 'updated_at', 'profil']

    def _resolve_relations(self, validated_data):
        """Convertit les identifiants de clés étrangères en instances (message d'erreur par champ)."""
        for field, model_cls in (('profil', Profil),):
            value = validated_data.get(field)
            if value is not None and not isinstance(value, model_cls):
                try:
                    validated_data[field] = model_cls.objects.get(pk=int(value))
                except (ValueError, TypeError, model_cls.DoesNotExist):
                    raise serializers.ValidationError({field: f"{model_cls.__name__} avec cet ID n'existe pas."})
        return validated_data

    def create(self, validated_data):
        """
        Crée une nouvelle instance de Experience.
        """
        return super().create(self._resolve_relations(validated_data))

    def update(self, instance, validated_data):
        """
        Met à jour une instance de Experience.
        """
        return super().update(instance, self._resolve_relations(validated_data))

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
        
        
        # Ajouter les données de la relation profil si elle existe
        if hasattr(instance, 'profil') and instance.profil:
            data['profil'] = {
                'id': instance.profil.id,
                '__str__': str(instance.profil),
            }
        else:
            data['profil'] = None
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class PrestationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les prestations.
    """
    
    class Meta:
        model = Prestation
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'title', 'slug', 'description', 'category', 'price', 'currency', 'delivery_days', 'revisions', 'cover_image', 'is_active', 'created_by', 'updated_by', 'created_at', 'updated_at', 'profil']

    def _resolve_relations(self, validated_data):
        """Convertit les identifiants de clés étrangères en instances (message d'erreur par champ)."""
        for field, model_cls in (('profil', Profil),):
            value = validated_data.get(field)
            if value is not None and not isinstance(value, model_cls):
                try:
                    validated_data[field] = model_cls.objects.get(pk=int(value))
                except (ValueError, TypeError, model_cls.DoesNotExist):
                    raise serializers.ValidationError({field: f"{model_cls.__name__} avec cet ID n'existe pas."})
        return validated_data

    def create(self, validated_data):
        """
        Crée une nouvelle instance de Prestation.
        """
        return super().create(self._resolve_relations(validated_data))

    def update(self, instance, validated_data):
        """
        Met à jour une instance de Prestation.
        """
        return super().update(instance, self._resolve_relations(validated_data))

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
        if getattr(instance, 'cover_image', None):
            data['cover_image_url'] = storage.url(getattr(instance, 'cover_image'))
        
        
        # Ajouter les données de la relation profil si elle existe
        if hasattr(instance, 'profil') and instance.profil:
            data['profil'] = {
                'id': instance.profil.id,
                '__str__': str(instance.profil),
            }
        else:
            data['profil'] = None
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class ProfilHistorySerializer(serializers.ModelSerializer):
    """
    Serializer pour les profil-histories.
    """
    
    class Meta:
        model = ProfilHistory
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'field', 'old_value', 'new_value', 'source', 'created_by', 'updated_by', 'created_at', 'updated_at', 'profil']

    def _resolve_relations(self, validated_data):
        """Convertit les identifiants de clés étrangères en instances (message d'erreur par champ)."""
        for field, model_cls in (('profil', Profil),):
            value = validated_data.get(field)
            if value is not None and not isinstance(value, model_cls):
                try:
                    validated_data[field] = model_cls.objects.get(pk=int(value))
                except (ValueError, TypeError, model_cls.DoesNotExist):
                    raise serializers.ValidationError({field: f"{model_cls.__name__} avec cet ID n'existe pas."})
        return validated_data

    def create(self, validated_data):
        """
        Crée une nouvelle instance de ProfilHistory.
        """
        return super().create(self._resolve_relations(validated_data))

    def update(self, instance, validated_data):
        """
        Met à jour une instance de ProfilHistory.
        """
        return super().update(instance, self._resolve_relations(validated_data))

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
        
        
        # Ajouter les données de la relation profil si elle existe
        if hasattr(instance, 'profil') and instance.profil:
            data['profil'] = {
                'id': instance.profil.id,
                '__str__': str(instance.profil),
            }
        else:
            data['profil'] = None
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class AvailabilitySerializer(serializers.ModelSerializer):
    """
    Serializer pour les availabilities.
    """
    
    class Meta:
        model = Availability
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'start_date', 'end_date', 'status', 'hours_per_week', 'source', 'note', 'created_by', 'updated_by', 'created_at', 'updated_at', 'profil']

    def _resolve_relations(self, validated_data):
        """Convertit les identifiants de clés étrangères en instances (message d'erreur par champ)."""
        for field, model_cls in (('profil', Profil),):
            value = validated_data.get(field)
            if value is not None and not isinstance(value, model_cls):
                try:
                    validated_data[field] = model_cls.objects.get(pk=int(value))
                except (ValueError, TypeError, model_cls.DoesNotExist):
                    raise serializers.ValidationError({field: f"{model_cls.__name__} avec cet ID n'existe pas."})
        return validated_data

    def create(self, validated_data):
        """
        Crée une nouvelle instance de Availability.
        """
        return super().create(self._resolve_relations(validated_data))

    def update(self, instance, validated_data):
        """
        Met à jour une instance de Availability.
        """
        return super().update(instance, self._resolve_relations(validated_data))

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
        
        
        # Ajouter les données de la relation profil si elle existe
        if hasattr(instance, 'profil') and instance.profil:
            data['profil'] = {
                'id': instance.profil.id,
                '__str__': str(instance.profil),
            }
        else:
            data['profil'] = None
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer pour les reviews.
    """
    
    class Meta:
        model = Review
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'rating', 'comment', 'is_public', 'created_by', 'updated_by', 'created_at', 'updated_at', 'target', 'author', 'candidature']
        depth = 1

    def _resolve_relations(self, validated_data):
        """Convertit les identifiants de clés étrangères en instances (message d'erreur par champ)."""
        for field, model_cls in (('target', Profil), ('author', Profil), ('candidature', Candidature),):
            value = validated_data.get(field)
            if value is not None and not isinstance(value, model_cls):
                try:
                    validated_data[field] = model_cls.objects.get(pk=int(value))
                except (ValueError, TypeError, model_cls.DoesNotExist):
                    raise serializers.ValidationError({field: f"{model_cls.__name__} avec cet ID n'existe pas."})
        return validated_data

    def create(self, validated_data):
        """
        Crée une nouvelle instance de Review.
        """
        return super().create(self._resolve_relations(validated_data))

    def update(self, instance, validated_data):
        """
        Met à jour une instance de Review.
        """
        return super().update(instance, self._resolve_relations(validated_data))

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
        
        
        # Ajouter les données de la relation target si elle existe
        if hasattr(instance, 'target') and instance.target:
            data['target'] = {
                'id': instance.target.id,
                '__str__': str(instance.target),
            }
        else:
            data['target'] = None
        
        
        # Ajouter les données de la relation author si elle existe
        if hasattr(instance, 'author') and instance.author:
            data['author'] = {
                'id': instance.author.id,
                '__str__': str(instance.author),
            }
        else:
            data['author'] = None
        
        
        # Ajouter les données de la relation candidature si elle existe
        if hasattr(instance, 'candidature') and instance.candidature:
            data['candidature'] = {
                'id': instance.candidature.id,
                '__str__': str(instance.candidature),
            }
        else:
            data['candidature'] = None
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class SwipeSerializer(serializers.ModelSerializer):
    """
    Serializer pour les swipes.
    """
    
    class Meta:
        model = Swipe
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'direction', 'context', 'created_by', 'updated_by', 'created_at', 'updated_at', 'author', 'target']
        depth = 1

    def _resolve_relations(self, validated_data):
        """Convertit les identifiants de clés étrangères en instances (message d'erreur par champ)."""
        for field, model_cls in (('author', Profil), ('target', Profil),):
            value = validated_data.get(field)
            if value is not None and not isinstance(value, model_cls):
                try:
                    validated_data[field] = model_cls.objects.get(pk=int(value))
                except (ValueError, TypeError, model_cls.DoesNotExist):
                    raise serializers.ValidationError({field: f"{model_cls.__name__} avec cet ID n'existe pas."})
        return validated_data

    def create(self, validated_data):
        """
        Crée une nouvelle instance de Swipe.
        """
        return super().create(self._resolve_relations(validated_data))

    def update(self, instance, validated_data):
        """
        Met à jour une instance de Swipe.
        """
        return super().update(instance, self._resolve_relations(validated_data))

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
        
        
        # Ajouter les données de la relation author si elle existe
        if hasattr(instance, 'author') and instance.author:
            data['author'] = {
                'id': instance.author.id,
                '__str__': str(instance.author),
            }
        else:
            data['author'] = None
        
        
        # Ajouter les données de la relation target si elle existe
        if hasattr(instance, 'target') and instance.target:
            data['target'] = {
                'id': instance.target.id,
                '__str__': str(instance.target),
            }
        else:
            data['target'] = None
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class ConnectionSerializer(serializers.ModelSerializer):
    """
    Serializer pour les connections.
    """
    
    class Meta:
        model = Connection
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = ['id', 'status', 'matched_at', 'created_by', 'updated_by', 'created_at', 'updated_at', 'profil_a', 'profil_b']
        depth = 1

    def _resolve_relations(self, validated_data):
        """Convertit les identifiants de clés étrangères en instances (message d'erreur par champ)."""
        for field, model_cls in (('profil_a', Profil), ('profil_b', Profil),):
            value = validated_data.get(field)
            if value is not None and not isinstance(value, model_cls):
                try:
                    validated_data[field] = model_cls.objects.get(pk=int(value))
                except (ValueError, TypeError, model_cls.DoesNotExist):
                    raise serializers.ValidationError({field: f"{model_cls.__name__} avec cet ID n'existe pas."})
        return validated_data

    def create(self, validated_data):
        """
        Crée une nouvelle instance de Connection.
        """
        return super().create(self._resolve_relations(validated_data))

    def update(self, instance, validated_data):
        """
        Met à jour une instance de Connection.
        """
        return super().update(instance, self._resolve_relations(validated_data))

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
        
        
        # Ajouter les données de la relation profil_a si elle existe
        if hasattr(instance, 'profil_a') and instance.profil_a:
            data['profil_a'] = {
                'id': instance.profil_a.id,
                '__str__': str(instance.profil_a),
            }
        else:
            data['profil_a'] = None
        
        
        # Ajouter les données de la relation profil_b si elle existe
        if hasattr(instance, 'profil_b') and instance.profil_b:
            data['profil_b'] = {
                'id': instance.profil_b.id,
                '__str__': str(instance.profil_b),
            }
        else:
            data['profil_b'] = None
        
        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class MeProfilWriteSerializer(serializers.ModelSerializer):
    """Champs du profil que l'utilisateur modifie lui-même (le compte, le slug et l'entreprise sont gérés par le service)."""

    class Meta:
        model = Profil
        fields = ['headline', 'bio', 'phone', 'country', 'city', 'remote', 'timezone', 'default_hours_per_week', 'is_open_to_work', 'daily_rate', 'currency', 'years_of_experience', 'languages', 'github_url', 'linkedin_url', 'portfolio_url', 'cv_visibility']

    def validate_country(self, value):
        if len(value) != 2 or not value.isalpha():
            raise serializers.ValidationError("Code pays ISO à 2 lettres attendu (ex. BF, SN).")
        return value.upper()


class MeCompanyWriteSerializer(serializers.ModelSerializer):
    """Champs de l'entreprise que son propriétaire modifie (vérification, slug et auteur restent côté serveur)."""

    class Meta:
        model = Company
        fields = ['name', 'description', 'sector', 'size', 'website', 'contact_email', 'phone', 'country', 'city', 'address']

    def validate_country(self, value):
        if len(value) != 2 or not value.isalpha():
            raise serializers.ValidationError("Code pays ISO à 2 lettres attendu (ex. BF, SN).")
        return value.upper()
