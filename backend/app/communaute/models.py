from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class AvisChoix(models.Model):
    """
    AvisChoix model.
    """

    membre = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='avis_choix',
    )
    option = models.ForeignKey(
        'OptionPublication',
        on_delete=models.CASCADE,
        related_name='avis',
    )
    explication = models.TextField()
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_avis_choix'
        verbose_name = 'Avis de choix'
        verbose_name_plural = 'Avis de choix'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return f"/communaute/avis-choix/{self.id}/"


class Commentaire(models.Model):
    """
    Commentaire model.
    """

    publication = models.ForeignKey(
        'Publication',
        on_delete=models.CASCADE,
        related_name='commentaires',
    )
    auteur = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='commentaires',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='reponses',
        null=True,
        blank=True,
    )
    option = models.ForeignKey(
        'OptionPublication',
        on_delete=models.SET_NULL,
        related_name='commentaires',
        null=True,
        blank=True,
        help_text='Option de débat concernée (publications CHOIX uniquement)',
    )
    nature = models.CharField(max_length=20, choices=[('COMMENTAIRE', 'Commentaire'), ('RETOUR_APP', 'Retour sur application'), ('REPONSE_TECHNIQUE', 'Réponse technique')])
    texte = models.TextField(blank=True, default='')
    est_anonyme = models.BooleanField(default=False)
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_commentaire'
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nature}"

    def get_absolute_url(self):
        return f"/communaute/commentaires/{self.id}/"


class MediaCommentaire(models.Model):
    """Média attaché à un commentaire (image, vidéo ou audio)."""

    KIND_IMAGE = 'IMAGE'
    KIND_VIDEO = 'VIDEO'
    KIND_AUDIO = 'AUDIO'
    KIND_CHOICES = (
        (KIND_IMAGE, 'Image'),
        (KIND_VIDEO, 'Vidéo'),
        (KIND_AUDIO, 'Audio'),
    )

    commentaire = models.ForeignKey(
        Commentaire,
        on_delete=models.CASCADE,
        related_name='medias',
    )
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    url = models.URLField()
    texte_alternatif = models.CharField(max_length=200, blank=True, default='')
    position = models.PositiveIntegerField(default=0)
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur",
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié",
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False,
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True,
    )

    class Meta:
        db_table = 'communaute_media_commentaire'
        verbose_name = 'Média de commentaire'
        verbose_name_plural = 'Médias de commentaire'
        ordering = ['position', 'id']

    def __str__(self):
        return f"{self.kind}:{self.id}"


class ConfirmationAide(models.Model):
    """
    ConfirmationAide model.
    """

    commentaire = models.ForeignKey(
        'Commentaire',
        on_delete=models.CASCADE,
        related_name='confirmations_aide',
    )
    membre = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='confirmations_aide',
    )
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_confirmation_aide'
        verbose_name = "Confirmation d'aide"
        verbose_name_plural = "Confirmations d'aide"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['commentaire', 'membre'],
                name='unique_confirmation_aide_commentaire_membre',
            ),
        ]

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return f"/communaute/confirmations-aide/{self.id}/"


class Conversation(models.Model):
    """
    Conversation privée entre deux membres (paire unique, ordre canonique).
    """

    membre_1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations_comme_membre_1',
    )
    membre_2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations_comme_membre_2',
    )
    membre_1_lu_at = models.DateTimeField(blank=True, null=True)
    membre_2_lu_at = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_conversation'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-updated_at', '-id']
        constraints = [
            models.UniqueConstraint(
                fields=['membre_1', 'membre_2'],
                name='uniq_conversation_paire',
            ),
            models.CheckConstraint(
                condition=models.Q(membre_1_id__lt=models.F('membre_2_id')),
                name='conversation_membre_1_lt_membre_2',
            ),
        ]

    def __str__(self):
        return f"Conversation {self.id}"

    def get_absolute_url(self):
        return f"/communaute/conversations/{self.id}/"

    def implique(self, user_id: int) -> bool:
        return user_id in (self.membre_1_id, self.membre_2_id)

    def autre_membre(self, user_id: int):
        if user_id == self.membre_1_id:
            return self.membre_2
        if user_id == self.membre_2_id:
            return self.membre_1
        return None


class Espace(models.Model):
    """
    Espace model.
    """
    
    type = models.CharField(max_length=20, choices=[('COMMUNAUTE', 'Communauté'), ('CHAINE', 'Chaîne')])
    nom = models.CharField(max_length=120)
    description = models.TextField(blank=True, default='')
    photo = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text='URL ou chemin de la photo de profil de l’espace',
    )
    acces = models.CharField(max_length=20, choices=[('PUBLIC', 'Public'), ('LIEN', 'Par lien')])
    membres_peuvent_publier = models.BooleanField(default=True)
    commentaires_ouverts = models.BooleanField(default=True)
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_espace'
        verbose_name = 'Espace'
        verbose_name_plural = 'Espaces'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type}"

    def get_absolute_url(self):
        return f"/communaute/espaces/{self.id}/"


class ImagePublication(models.Model):
    """
    Média attaché à une publication (image ou vidéo).
    """

    KIND_IMAGE = 'IMAGE'
    KIND_VIDEO = 'VIDEO'
    KIND_CHOICES = (
        (KIND_IMAGE, 'Image'),
        (KIND_VIDEO, 'Vidéo'),
    )

    publication = models.ForeignKey(
        'Publication',
        on_delete=models.CASCADE,
        related_name='images',
    )
    kind = models.CharField(
        max_length=10,
        choices=KIND_CHOICES,
        default=KIND_IMAGE,
    )
    url = models.URLField()
    texte_alternatif = models.CharField(max_length=200, blank=True, default='')
    position = models.PositiveIntegerField(default=0)
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_image_publication'
        verbose_name = 'Image de publication'
        verbose_name_plural = 'Images de publication'
        ordering = ['position', 'id']

    def __str__(self):
        return f"{self.texte_alternatif}"

    def get_absolute_url(self):
        return f"/communaute/images-publication/{self.id}/"


class LienInvitation(models.Model):
    """
    Lien d'invitation révocable pour rejoindre un espace en accès LIEN.
    """

    espace = models.ForeignKey(
        'Espace',
        on_delete=models.CASCADE,
        related_name='liens_invitation',
    )
    cree_par = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='liens_invitation_crees',
    )
    code_hash = models.CharField(max_length=128, unique=True)
    previsualisation_autorisee = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_lien_invitation'
        verbose_name = "Lien d'invitation"
        verbose_name_plural = "Liens d'invitation"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code_hash}"

    @property
    def est_actif(self) -> bool:
        return self.revoked_at is None

    def get_absolute_url(self):
        return f"/communaute/liens-invitation/{self.id}/"


class LikeCommentaire(models.Model):
    """
    LikeCommentaire model.
    """

    commentaire = models.ForeignKey(
        Commentaire,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    membre = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes_commentaire',
    )
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_like_commentaire'
        verbose_name = 'Like de commentaire'
        verbose_name_plural = 'Likes de commentaire'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['commentaire', 'membre'],
                name='unique_like_commentaire_membre',
            )
        ]

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return f"/communaute/likes-commentaire/{self.id}/"


class LikePublication(models.Model):
    """
    LikePublication model.
    """

    publication = models.ForeignKey(
        'Publication',
        on_delete=models.CASCADE,
        related_name='likes',
    )
    membre = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes_publication',
    )
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_like_publication'
        verbose_name = 'Like de publication'
        verbose_name_plural = 'Likes de publication'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['publication', 'membre'],
                name='unique_like_publication_membre',
            )
        ]

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return f"/communaute/likes-publication/{self.id}/"


class FavoriPublication(models.Model):
    """
    Publication enregistrée (bookmark) par un membre.
    """

    publication = models.ForeignKey(
        'Publication',
        on_delete=models.CASCADE,
        related_name='favoris',
    )
    membre = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoris_publication',
    )
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur",
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié",
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False,
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True,
    )

    class Meta:
        db_table = 'communaute_favori_publication'
        verbose_name = 'Favori de publication'
        verbose_name_plural = 'Favoris de publication'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['publication', 'membre'],
                name='unique_favori_publication_membre',
            )
        ]

    def __str__(self):
        return f"FavoriPublication {self.id}"


class Message(models.Model):
    """
    Message texte dans une conversation privée.
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    auteur = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='messages_prives',
    )
    texte = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_message'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['sent_at', 'id']

    def __str__(self):
        return f"Message {self.id}"

    def get_absolute_url(self):
        return f"/communaute/messages/{self.id}/"


class MessageGroupe(models.Model):
    """
    Message de discussion dans une communauté (chat de groupe).
    """

    espace = models.ForeignKey(
        'Espace',
        on_delete=models.CASCADE,
        related_name='messages_groupe',
    )
    auteur = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='messages_groupe',
    )
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reponses',
    )
    texte = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    supprime_at = models.DateTimeField(null=True, blank=True)
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur",
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié",
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False,
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True,
    )

    class Meta:
        db_table = 'communaute_message_groupe'
        verbose_name = 'Message de groupe'
        verbose_name_plural = 'Messages de groupe'
        ordering = ['sent_at', 'id']

    def __str__(self):
        return f"MessageGroupe {self.id}"


class ReactionMessageGroupe(models.Model):
    """
    Réaction emoji sur un message de groupe (style WhatsApp).
    """

    message = models.ForeignKey(
        MessageGroupe,
        on_delete=models.CASCADE,
        related_name='reactions',
    )
    membre = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reactions_message_groupe',
    )
    emoji = models.CharField(max_length=8)
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur",
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié",
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False,
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True,
    )

    class Meta:
        db_table = 'communaute_reaction_message_groupe'
        verbose_name = 'Réaction message de groupe'
        verbose_name_plural = 'Réactions messages de groupe'
        constraints = [
            models.UniqueConstraint(
                fields=['message', 'membre'],
                name='unique_reaction_message_groupe_membre',
            )
        ]

    def __str__(self):
        return f"ReactionMessageGroupe {self.id}"


class NotificationResume(models.Model):
    """
    Résumé quotidien des nouveautés d'abonnements pour un membre.
    """

    destinataire = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications_resume',
    )
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    nombre_nouveautes = models.PositiveIntegerField(default=0)
    read_at = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_notification_resume'
        verbose_name = 'Résumé de notification'
        verbose_name_plural = 'Résumés de notification'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['destinataire', 'periode_debut'],
                name='uniq_notification_resume_destinataire_jour',
            ),
        ]

    def __str__(self):
        return f"Resume {self.destinataire_id} {self.periode_debut}"

    def get_absolute_url(self):
        return f"/communaute/notifications-resume/{self.id}/"


class OptionPublication(models.Model):
    """
    OptionPublication model.
    """

    publication = models.ForeignKey(
        'Publication',
        on_delete=models.CASCADE,
        related_name='options',
    )
    libelle = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    image_url = models.URLField(blank=True, default='')
    position = models.PositiveIntegerField(default=0)
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_option_publication'
        verbose_name = 'Option de publication'
        verbose_name_plural = 'Options de publication'
        ordering = ['position', 'id']

    def __str__(self):
        return f"{self.libelle}"

    def get_absolute_url(self):
        return f"/communaute/options-publication/{self.id}/"


class ParticipationEspace(models.Model):
    """
    Participation d'un membre à une communauté ou chaîne.
    """

    ROLE_SUPER_ADMIN = 'SUPER_ADMIN'
    ROLE_ADMIN = 'ADMIN'
    ROLE_MEMBRE = 'MEMBRE'

    espace = models.ForeignKey(
        'Espace',
        on_delete=models.CASCADE,
        related_name='participations',
    )
    membre = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='participations_espace',
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ('SUPER_ADMIN', 'Super administrateur'),
            ('ADMIN', 'Administrateur'),
            ('MEMBRE', 'Membre'),
        ],
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    lu_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Dernière visite (chat communauté ou fil chaîne)',
    )
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_participation_espace'
        verbose_name = 'Participation à un espace'
        verbose_name_plural = 'Participations aux espaces'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['espace', 'membre'],
                name='uniq_participation_espace_membre',
            ),
        ]

    def __str__(self):
        return f"{self.role}"

    def get_absolute_url(self):
        return f"/communaute/participations-espace/{self.id}/"


class Publication(models.Model):
    """
    Publication model.
    """
    
    auteur = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='publications',
    )
    espace = models.ForeignKey(
        'Espace',
        on_delete=models.SET_NULL,
        related_name='publications',
        blank=True,
        null=True,
        help_text='Espace (communauté/chaîne) ; null = fil général',
    )
    type = models.CharField(max_length=20, choices=[('DISCUSSION', 'Discussion'), ('APPLICATION', 'Application'), ('ENTRAIDE', 'Entraide technique'), ('CHOIX', 'Aide au choix'), ('SONDAGE', 'Sondage')])
    titre = models.CharField(max_length=200)
    description = models.TextField()
    lien_app = models.URLField(blank=True, default='')
    plateforme_app = models.CharField(max_length=20, blank=True, default='', choices=[('WEB', 'Web'), ('MOBILE', 'Mobile'), ('LES_DEUX', 'Web et mobile')])
    contraintes = models.TextField(blank=True, default='')
    justification_finale = models.TextField(blank=True, default='')
    decided_at = models.DateTimeField(blank=True, null=True)
    mode_vote = models.CharField(max_length=20, blank=True, default='', choices=[('UNIQUE', 'Choix unique'), ('MULTIPLE', 'Choix multiple')])
    votes_fermes_at = models.DateTimeField(blank=True, null=True)
    reponse_acceptee = models.ForeignKey(
        'Commentaire',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publications_acceptees',
    )
    option_retenue = models.ForeignKey(
        'OptionPublication',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publications_retenues',
    )
    hub_request_key = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        unique=True,
        help_text="Clé d'idempotence DevStreet Hub (ProjectDiscussionLink.request_key)",
    )
    projet_id = models.IntegerField(
        blank=True,
        null=True,
        db_index=True,
        help_text="Projet Hub lié (dénormalisé depuis ProjectDiscussionLink)",
    )
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_publication'
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type}"

    def get_absolute_url(self):
        return f"/communaute/publications/{self.id}/"


class SuiviUtilisateur(models.Model):
    """
    Relation de suivi entre deux membres (suiveur → suivi).
    """

    suiveur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='suivis_emis',
    )
    suivi = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='suivis_recus',
    )
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_suivi_utilisateur'
        verbose_name = "Suivi d'utilisateur"
        verbose_name_plural = "Suivis d'utilisateurs"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['suiveur', 'suivi'],
                name='uniq_suivi_suiveur_suivi',
            ),
        ]

    def __str__(self):
        return f"{self.suiveur_id} → {self.suivi_id}"

    def get_absolute_url(self):
        return f"/communaute/suivis-utilisateur/{self.id}/"


class VoteSondage(models.Model):
    """
    VoteSondage model.
    """
    
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'communaute_vote_sondage'
        verbose_name = 'Vote de sondage'
        verbose_name_plural = 'Votes de sondage'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return f"/communaute/votes-sondage/{self.id}/" 
