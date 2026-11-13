from rest_framework import serializers
from collections import Counter

from app.communaute.models import AvisChoix, Commentaire, ConfirmationAide, Conversation, Espace, ImagePublication, LienInvitation, LikeCommentaire, LikePublication, MediaCommentaire, Message, MessageGroupe, NotificationResume, OptionPublication, ParticipationEspace, Publication, SuiviUtilisateur, VoteSondage


def public_user_payload(user):
    """Profil public minimal (id, noms, photo) pour les auteurs exposés à l'API."""
    if user is None:
        return None
    return {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'photo': (getattr(user, 'photo', None) or '') or '',
    }


class AvisChoixMembreSerializer(serializers.Serializer):
    """Profil public minimal de l'auteur d'un avis."""

    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    photo = serializers.CharField(required=False, allow_blank=True)


class AvisChoixSerializer(serializers.ModelSerializer):
    """
    Serializer pour les avis-choix.
    """

    membre = AvisChoixMembreSerializer(read_only=True)
    option = serializers.PrimaryKeyRelatedField(read_only=True)
    option_id = serializers.IntegerField(write_only=True, required=True)
    explication = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = AvisChoix
        fields = [
            'id',
            'membre',
            'option',
            'option_id',
            'explication',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_fields(self):
        fields = super().get_fields()
        for sys_field in ['id', 'membre', 'option', 'created_by', 'updated_by', 'created_at', 'updated_at']:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = instance.created_at.isoformat() if hasattr(instance, 'created_at') else None
        data['updated_at'] = instance.updated_at.isoformat() if hasattr(instance, 'updated_at') else None
        if instance.membre_id:
            data['membre'] = public_user_payload(instance.membre)
        return data

    def validate(self, data):
        return data


class CommentaireAuteurSerializer(serializers.Serializer):
    """Profil public minimal de l'auteur d'un commentaire."""

    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    photo = serializers.CharField(required=False, allow_blank=True)


class MediaCommentaireSerializer(serializers.ModelSerializer):
    """Média attaché à un commentaire."""

    class Meta:
        model = MediaCommentaire
        fields = [
            'id',
            'commentaire',
            'kind',
            'url',
            'texte_alternatif',
            'position',
        ]
        read_only_fields = fields


class MediaCommentaireWriteSerializer(serializers.Serializer):
    """Payload d'écriture d'un média de commentaire."""

    url = serializers.URLField()
    kind = serializers.ChoiceField(
        choices=['IMAGE', 'VIDEO', 'AUDIO'], required=False, default='IMAGE'
    )
    texte_alternatif = serializers.CharField(
        max_length=200, required=False, allow_blank=True, default=''
    )
    position = serializers.IntegerField(required=False, min_value=0, default=0)


class CommentaireSerializer(serializers.ModelSerializer):
    """
    Serializer pour les commentaires.
    """

    auteur = CommentaireAuteurSerializer(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    publication = serializers.PrimaryKeyRelatedField(read_only=True)
    publication_id = serializers.IntegerField(write_only=True, required=False)
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    option = serializers.PrimaryKeyRelatedField(read_only=True)
    option_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    option_libelle = serializers.SerializerMethodField()
    est_anonyme = serializers.BooleanField(required=False, default=False)
    likes_count = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()
    confirmations_count = serializers.SerializerMethodField()
    confirmed_by_me = serializers.SerializerMethodField()
    reponses = serializers.SerializerMethodField()
    medias = MediaCommentaireSerializer(many=True, read_only=True)
    medias_data = MediaCommentaireWriteSerializer(
        many=True, write_only=True, required=False, default=list
    )

    class Meta:
        model = Commentaire
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = [
            'id',
            'publication',
            'publication_id',
            'auteur',
            'parent',
            'parent_id',
            'option',
            'option_id',
            'option_libelle',
            'nature',
            'texte',
            'est_anonyme',
            'medias',
            'medias_data',
            'likes_count',
            'liked_by_me',
            'confirmations_count',
            'confirmed_by_me',
            'reponses',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_fields(self):
        """
        Marque les champs système en lecture seule s'ils existent.
        """
        fields = super().get_fields()
        for sys_field in [
            'id',
            'auteur',
            'publication',
            'parent',
            'option',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]:
            if sys_field in fields:
                fields[sys_field].read_only = True
        if 'nature' in fields:
            fields['nature'].required = False
        if 'texte' in fields:
            fields['texte'].required = False
            fields['texte'].allow_blank = True
        return fields

    def get_option_libelle(self, instance):
        option = getattr(instance, 'option', None)
        if option is None:
            return None
        return option.libelle

    def get_likes_count(self, instance):
        return int(getattr(instance, 'likes_count', 0) or 0)

    def get_liked_by_me(self, instance):
        return bool(getattr(instance, 'liked_by_me', 0))

    def get_confirmations_count(self, instance):
        return int(getattr(instance, 'confirmations_count', 0) or 0)

    def get_confirmed_by_me(self, instance):
        return bool(getattr(instance, 'confirmed_by_me', 0))

    def get_reponses(self, instance):
        if instance.parent_id is not None:
            return []
        reponses = getattr(instance, 'reponses', None)
        if reponses is None:
            return []
        # Prefetch renvoie un manager lié ; list() matérialise l'ordre
        children = list(reponses.all()) if hasattr(reponses, 'all') else list(reponses)
        return CommentaireSerializer(children, many=True, context=self.context).data

    def to_representation(self, instance):
        """
        Personnalise la représentation des données.
        Un retour anonyme n'expose jamais l'identité, même dans les objets imbriqués.
        """
        data = super().to_representation(instance)

        data['created_at'] = instance.created_at.isoformat() if hasattr(instance, 'created_at') else None
        data['updated_at'] = instance.updated_at.isoformat() if hasattr(instance, 'updated_at') else None
        if instance.est_anonyme:
            data['auteur'] = None
            data['est_anonyme'] = True
            # Ne pas laisser fuiter created_by / updated_by pour un retour anonyme
            data.pop('created_by', None)
            data.pop('updated_by', None)
        elif instance.auteur_id:
            data['auteur'] = public_user_payload(instance.auteur)

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

    commentaire = serializers.PrimaryKeyRelatedField(read_only=True)
    membre = serializers.PrimaryKeyRelatedField(read_only=True)
    commentaire_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = ConfirmationAide
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = [
            'id',
            'commentaire',
            'commentaire_id',
            'membre',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

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


class ConversationMembreSerializer(serializers.Serializer):
    """Profil public minimal d'un membre de conversation."""

    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    photo = serializers.CharField(required=False, allow_blank=True)


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer pour les conversations privées."""

    membre_1 = ConversationMembreSerializer(read_only=True)
    membre_2 = ConversationMembreSerializer(read_only=True)
    destinataire_id = serializers.IntegerField(write_only=True, required=True)
    autre_membre = serializers.SerializerMethodField()
    dernier_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id',
            'membre_1',
            'membre_2',
            'destinataire_id',
            'autre_membre',
            'dernier_message',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_fields(self):
        fields = super().get_fields()
        for sys_field in [
            'id',
            'membre_1',
            'membre_2',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def _membre_payload(self, user):
        return public_user_payload(user)

    def get_autre_membre(self, instance):
        request = self.context.get('request')
        if request is None or not getattr(request.user, 'id', None):
            return None
        return self._membre_payload(instance.autre_membre(request.user.id))

    def get_dernier_message(self, instance):
        message = (
            instance.messages.order_by('-sent_at', '-id')
            .select_related('auteur')
            .first()
        )
        if message is None:
            return None
        return {
            'id': message.id,
            'texte': message.texte,
            'sent_at': message.sent_at.isoformat() if message.sent_at else None,
            'auteur_id': message.auteur_id,
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = instance.created_at.isoformat() if instance.created_at else None
        data['updated_at'] = instance.updated_at.isoformat() if instance.updated_at else None
        data['membre_1'] = self._membre_payload(instance.membre_1)
        data['membre_2'] = self._membre_payload(instance.membre_2)
        return data

    def validate(self, data):
        return data


class EspaceSerializer(serializers.ModelSerializer):
    """
    Serializer pour les espaces.
    """

    mon_role = serializers.SerializerMethodField()
    membres_count = serializers.SerializerMethodField()

    class Meta:
        model = Espace
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = [
            'id',
            'type',
            'nom',
            'description',
            'photo',
            'acces',
            'membres_peuvent_publier',
            'commentaires_ouverts',
            'mon_role',
            'membres_count',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_fields(self):
        """
        Marque les champs système en lecture seule s'ils existent.
        """
        fields = super().get_fields()
        for sys_field in [
            'id',
            'type',
            'acces',
            'mon_role',
            'membres_count',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def get_mon_role(self, instance):
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        if not user or not getattr(user, 'is_authenticated', False) or not user.id:
            return None
        cache = self.context.setdefault('_mon_role_by_espace', {})
        if instance.id not in cache:
            from app.communaute.models import ParticipationEspace

            cache[instance.id] = (
                ParticipationEspace.objects.filter(
                    espace_id=instance.id, membre_id=user.id
                )
                .values_list('role', flat=True)
                .first()
            )
        return cache[instance.id]

    def get_membres_count(self, instance):
        annotated = getattr(instance, 'membres_count', None)
        if annotated is not None:
            return int(annotated)
        return instance.participations.count()

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
    Serializer pour les médias de publication (image / vidéo).
    """

    class Meta:
        model = ImagePublication
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = [
            'id',
            'publication',
            'kind',
            'url',
            'texte_alternatif',
            'position',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

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


class PublicationAuteurSerializer(serializers.Serializer):
    """Profil public minimal de l'auteur d'une publication."""

    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    photo = serializers.CharField(required=False, allow_blank=True)


class PublicationImageWriteSerializer(serializers.Serializer):
    """Média (image ou vidéo) fourni à la création d'une publication."""

    url = serializers.URLField()
    kind = serializers.ChoiceField(
        choices=['IMAGE', 'VIDEO'], required=False, default='IMAGE'
    )
    texte_alternatif = serializers.CharField(
        max_length=200, required=False, allow_blank=True, default=''
    )
    position = serializers.IntegerField(required=False, min_value=0, default=0)


class LienInvitationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les liens-invitation (sans code brut).
    """

    est_actif = serializers.SerializerMethodField()

    class Meta:
        model = LienInvitation
        fields = [
            'id',
            'espace',
            'cree_par',
            'previsualisation_autorisee',
            'revoked_at',
            'est_actif',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_fields(self):
        fields = super().get_fields()
        for sys_field in [
            'id',
            'espace',
            'cree_par',
            'est_actif',
            'revoked_at',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def get_est_actif(self, instance):
        return instance.revoked_at is None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = instance.created_at.isoformat() if hasattr(instance, 'created_at') else None
        data['updated_at'] = instance.updated_at.isoformat() if hasattr(instance, 'updated_at') else None
        data['revoked_at'] = (
            instance.revoked_at.isoformat() if instance.revoked_at else None
        )
        return data

    def validate(self, data):
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


class MessageGroupeSerializer(serializers.ModelSerializer):
    """Serializer pour les messages de chat de communauté."""

    auteur = ConversationMembreSerializer(read_only=True)
    reply_to_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = MessageGroupe
        fields = [
            'id',
            'espace',
            'auteur',
            'texte',
            'reply_to_id',
            'sent_at',
            'supprime_at',
            'created_at',
            'updated_at',
        ]

    def get_fields(self):
        fields = super().get_fields()
        for sys_field in [
            'id',
            'espace',
            'auteur',
            'sent_at',
            'supprime_at',
            'created_at',
            'updated_at',
        ]:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def _reply_preview(self, reply):
        if reply is None:
            return None
        auteur = public_user_payload(reply.auteur) if reply.auteur_id else None
        if reply.supprime_at is not None:
            return {
                'id': reply.id,
                'texte': '',
                'supprime': True,
                'auteur': auteur,
            }
        preview = (reply.texte or '')[:160]
        return {
            'id': reply.id,
            'texte': preview,
            'supprime': False,
            'auteur': auteur,
        }

    def _reactions_payload(self, instance):
        request = self.context.get('request')
        viewer_id = (
            request.user.id
            if request is not None and getattr(request, 'user', None)
            and request.user.is_authenticated
            else None
        )
        reactions = list(instance.reactions.all())
        counts = Counter(r.emoji for r in reactions)
        ma_reaction = next(
            (r.emoji for r in reactions if r.membre_id == viewer_id),
            None,
        )
        return {
            'counts': [
                {'emoji': emoji, 'count': count}
                for emoji, count in sorted(
                    counts.items(), key=lambda item: (-item[1], item[0])
                )
            ],
            'ma_reaction': ma_reaction,
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        deleted = instance.supprime_at is not None
        data['texte'] = '' if deleted else instance.texte
        data['supprime'] = deleted
        data['sent_at'] = instance.sent_at.isoformat() if instance.sent_at else None
        data['supprime_at'] = (
            instance.supprime_at.isoformat() if instance.supprime_at else None
        )
        data['created_at'] = (
            instance.created_at.isoformat() if instance.created_at else None
        )
        data['updated_at'] = (
            instance.updated_at.isoformat() if instance.updated_at else None
        )
        if instance.auteur_id:
            data['auteur'] = public_user_payload(instance.auteur)
        data['reply_to'] = self._reply_preview(instance.reply_to)
        data['reactions'] = self._reactions_payload(instance)
        return data


class MessageSerializer(serializers.ModelSerializer):
    """Serializer pour les messages privés."""

    auteur = ConversationMembreSerializer(read_only=True)
    conversation = serializers.PrimaryKeyRelatedField(read_only=True)
    conversation_id = serializers.IntegerField(write_only=True, required=True)
    texte = serializers.CharField(required=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'conversation_id',
            'auteur',
            'texte',
            'sent_at',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_fields(self):
        fields = super().get_fields()
        for sys_field in [
            'id',
            'conversation',
            'auteur',
            'sent_at',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sent_at'] = instance.sent_at.isoformat() if instance.sent_at else None
        data['created_at'] = instance.created_at.isoformat() if instance.created_at else None
        data['updated_at'] = instance.updated_at.isoformat() if instance.updated_at else None
        if instance.auteur_id:
            data['auteur'] = public_user_payload(instance.auteur)
        return data

    def validate(self, data):
        return data


class NotificationResumeSerializer(serializers.ModelSerializer):
    """
    Serializer pour les résumés quotidiens d'abonnements.
    """

    class Meta:
        model = NotificationResume
        fields = [
            'id',
            'destinataire',
            'periode_debut',
            'periode_fin',
            'nombre_nouveautes',
            'read_at',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_fields(self):
        fields = super().get_fields()
        for sys_field in [
            'id',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
            'read_at',
        ]:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = (
            instance.created_at.isoformat()
            if getattr(instance, 'created_at', None)
            else None
        )
        data['updated_at'] = (
            instance.updated_at.isoformat()
            if getattr(instance, 'updated_at', None)
            else None
        )
        data['read_at'] = (
            instance.read_at.isoformat()
            if getattr(instance, 'read_at', None)
            else None
        )
        periode_debut = getattr(instance, 'periode_debut', None)
        periode_fin = getattr(instance, 'periode_fin', None)
        data['periode_debut'] = (
            periode_debut.isoformat()
            if hasattr(periode_debut, 'isoformat')
            else periode_debut
        )
        data['periode_fin'] = (
            periode_fin.isoformat()
            if hasattr(periode_fin, 'isoformat')
            else periode_fin
        )
        return data

    def validate(self, data):
        return data


class OptionPublicationWriteSerializer(serializers.Serializer):
    """Payload d'écriture d'une option pour une aide au choix."""

    libelle = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    image_url = serializers.URLField(required=False, allow_blank=True, default='')
    position = serializers.IntegerField(required=False, min_value=0, default=0)


class OptionPublicationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les options-publication.
    """

    publication = serializers.PrimaryKeyRelatedField(read_only=True)
    avis_count = serializers.SerializerMethodField()

    class Meta:
        model = OptionPublication
        fields = [
            'id',
            'publication',
            'libelle',
            'description',
            'image_url',
            'position',
            'avis_count',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_fields(self):
        fields = super().get_fields()
        for sys_field in ['id', 'publication', 'created_by', 'updated_by', 'created_at', 'updated_at']:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def get_avis_count(self, instance):
        return int(getattr(instance, 'avis_count', 0) or 0)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = instance.created_at.isoformat() if hasattr(instance, 'created_at') else None
        data['updated_at'] = instance.updated_at.isoformat() if hasattr(instance, 'updated_at') else None
        return data

    def validate(self, data):
        return data


class ParticipationEspaceSerializer(serializers.ModelSerializer):
    """
    Serializer pour les participations-espace.
    """

    membre_detail = serializers.SerializerMethodField()

    class Meta:
        model = ParticipationEspace
        fields = [
            'id',
            'espace',
            'membre',
            'membre_detail',
            'role',
            'joined_at',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_fields(self):
        fields = super().get_fields()
        for sys_field in [
            'id',
            'espace',
            'membre',
            'membre_detail',
            'role',
            'joined_at',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def get_membre_detail(self, instance):
        membre = getattr(instance, 'membre', None)
        if membre is None:
            return None
        full_name = f"{getattr(membre, 'first_name', '')} {getattr(membre, 'last_name', '')}".strip()
        return {
            'id': membre.id,
            'username': getattr(membre, 'username', ''),
            'full_name': full_name or getattr(membre, 'username', ''),
            'photo': getattr(membre, 'photo', '') or '',
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = instance.created_at.isoformat() if hasattr(instance, 'created_at') else None
        data['updated_at'] = instance.updated_at.isoformat() if hasattr(instance, 'updated_at') else None
        data['joined_at'] = instance.joined_at.isoformat() if getattr(instance, 'joined_at', None) else None
        return data

    def validate(self, data):
        return data


class PublicationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les publications.
    """

    auteur = PublicationAuteurSerializer(read_only=True)
    images = ImagePublicationSerializer(many=True, read_only=True)
    images_data = PublicationImageWriteSerializer(
        many=True, write_only=True, required=False, default=list
    )
    options = OptionPublicationSerializer(many=True, read_only=True)
    options_data = OptionPublicationWriteSerializer(
        many=True, write_only=True, required=False, default=list
    )
    option_retenue = serializers.PrimaryKeyRelatedField(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()
    saved_by_me = serializers.SerializerMethodField()
    following_auteur = serializers.SerializerMethodField()
    mon_avis_option_id = serializers.SerializerMethodField()
    projet = serializers.SerializerMethodField()
    espace = serializers.SerializerMethodField()
    espace_id = serializers.IntegerField(required=False, allow_null=True)
    type = serializers.ChoiceField(
        choices=[
            ('DISCUSSION', 'Discussion'),
            ('APPLICATION', 'Application'),
            ('ENTRAIDE', 'Entraide technique'),
            ('CHOIX', 'Aide au choix'),
            ('SONDAGE', 'Sondage'),
        ],
        required=False,
        default='DISCUSSION',
    )

    class Meta:
        model = Publication
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = [
            'id',
            'auteur',
            'type',
            'titre',
            'description',
            'lien_app',
            'plateforme_app',
            'contraintes',
            'justification_finale',
            'decided_at',
            'mode_vote',
            'votes_fermes_at',
            'reponse_acceptee',
            'option_retenue',
            'options',
            'options_data',
            'images',
            'images_data',
            'likes_count',
            'comments_count',
            'liked_by_me',
            'saved_by_me',
            'following_auteur',
            'mon_avis_option_id',
            'projet',
            'projet_id',
            'espace',
            'espace_id',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_fields(self):
        """
        Marque les champs système en lecture seule s'ils existent.
        """
        fields = super().get_fields()
        for sys_field in [
            'id',
            'auteur',
            'reponse_acceptee',
            'option_retenue',
            'options',
            'projet',
            'projet_id',
            'espace',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]:
            if sys_field in fields:
                fields[sys_field].read_only = True
        # Champs propres aux autres types : non requis pour une discussion
        for optional_field in [
            'lien_app',
            'plateforme_app',
            'contraintes',
            'justification_finale',
            'decided_at',
            'mode_vote',
            'votes_fermes_at',
            'espace_id',
        ]:
            if optional_field in fields:
                fields[optional_field].required = False
        return fields

    def get_projet(self, instance):
        projet_id = getattr(instance, 'projet_id', None)
        if not projet_id:
            return None
        cache = self.context.setdefault('projets_by_id', {})
        if projet_id not in cache:
            from django.apps import apps

            Project = apps.get_model('projects', 'Project')
            row = (
                Project.objects.filter(pk=projet_id)
                .values('id', 'title', 'slug')
                .first()
            )
            cache[projet_id] = (
                {
                    'id': row['id'],
                    'titre': row['title'],
                    'slug': row['slug'],
                }
                if row
                else {'id': projet_id, 'titre': None, 'slug': None}
            )
        return cache[projet_id]

    def get_espace(self, instance):
        espace = getattr(instance, 'espace', None)
        if espace is None:
            return None
        return {
            'id': espace.id,
            'nom': espace.nom,
            'type': espace.type,
            'acces': getattr(espace, 'acces', 'PUBLIC'),
            'commentaires_ouverts': bool(espace.commentaires_ouverts),
            'joined_by_me': bool(getattr(instance, 'joined_espace', False)),
        }

    def get_mon_avis_option_id(self, instance):
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        if not user or not getattr(user, 'is_authenticated', False) or not user.id:
            return None
        avis = (
            AvisChoix.objects.filter(membre_id=user.id, option__publication_id=instance.id)
            .values_list('option_id', flat=True)
            .first()
        )
        return avis

    def get_likes_count(self, instance):
        return int(getattr(instance, 'likes_count', 0) or 0)

    def get_comments_count(self, instance):
        return int(getattr(instance, 'comments_count', 0) or 0)

    def get_liked_by_me(self, instance):
        return bool(getattr(instance, 'liked_by_me', 0))

    def get_saved_by_me(self, instance):
        return bool(getattr(instance, 'saved_by_me', 0))

    def get_following_auteur(self, instance):
        return bool(getattr(instance, 'following_auteur', False))

    def to_representation(self, instance):
        """
        Personnalise la représentation des données.
        """
        data = super().to_representation(instance)

        data['created_at'] = instance.created_at.isoformat() if hasattr(instance, 'created_at') else None
        data['updated_at'] = instance.updated_at.isoformat() if hasattr(instance, 'updated_at') else None
        if instance.auteur_id:
            data['auteur'] = public_user_payload(instance.auteur)
        else:
            data['auteur'] = None

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
        fields = [
            'id',
            'suiveur',
            'suivi',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_fields(self):
        fields = super().get_fields()
        for sys_field in [
            'id',
            'suiveur',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = (
            instance.created_at.isoformat() if instance.created_at else None
        )
        data['updated_at'] = (
            instance.updated_at.isoformat() if instance.updated_at else None
        )
        return data

    def validate(self, data):
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
