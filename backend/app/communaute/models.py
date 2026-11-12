from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class AvisChoix(models.Model):
    """
    AvisChoix model.
    """
    
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
    
    nature = models.CharField(max_length=20, choices=[('COMMENTAIRE', 'Commentaire'), ('RETOUR_APP', 'Retour sur application'), ('REPONSE_TECHNIQUE', 'Réponse technique')])
    texte = models.TextField()
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


class ConfirmationAide(models.Model):
    """
    ConfirmationAide model.
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
        db_table = 'communaute_confirmation_aide'
        verbose_name = "Confirmation d'aide"
        verbose_name_plural = "Confirmations d'aide"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return f"/communaute/confirmations-aide/{self.id}/"


class Conversation(models.Model):
    """
    Conversation model.
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
        db_table = 'communaute_conversation'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return f"/communaute/conversations/{self.id}/"


class Espace(models.Model):
    """
    Espace model.
    """
    
    type = models.CharField(max_length=20, choices=[('COMMUNAUTE', 'Communauté'), ('CHAINE', 'Chaîne')])
    nom = models.CharField(max_length=120)
    description = models.TextField(blank=True, default='')
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
    ImagePublication model.
    """
    
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
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.texte_alternatif}"

    def get_absolute_url(self):
        return f"/communaute/images-publication/{self.id}/"


class LienInvitation(models.Model):
    """
    LienInvitation model.
    """
    
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

    def get_absolute_url(self):
        return f"/communaute/liens-invitation/{self.id}/"


class LikeCommentaire(models.Model):
    """
    LikeCommentaire model.
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
        db_table = 'communaute_like_commentaire'
        verbose_name = 'Like de commentaire'
        verbose_name_plural = 'Likes de commentaire'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return f"/communaute/likes-commentaire/{self.id}/"


class LikePublication(models.Model):
    """
    LikePublication model.
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
        db_table = 'communaute_like_publication'
        verbose_name = 'Like de publication'
        verbose_name_plural = 'Likes de publication'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return f"/communaute/likes-publication/{self.id}/"


class Message(models.Model):
    """
    Message model.
    """
    
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
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return f"/communaute/messages/{self.id}/"


class NotificationResume(models.Model):
    """
    NotificationResume model.
    """
    
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

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return f"/communaute/notifications-resume/{self.id}/"


class OptionPublication(models.Model):
    """
    OptionPublication model.
    """
    
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
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.libelle}"

    def get_absolute_url(self):
        return f"/communaute/options-publication/{self.id}/"


class ParticipationEspace(models.Model):
    """
    ParticipationEspace model.
    """
    
    role = models.CharField(max_length=20, choices=[('SUPER_ADMIN', 'Super administrateur'), ('ADMIN', 'Administrateur'), ('MEMBRE', 'Membre')])
    joined_at = models.DateTimeField(auto_now_add=True)
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

    def __str__(self):
        return f"{self.role}"

    def get_absolute_url(self):
        return f"/communaute/participations-espace/{self.id}/"


class Publication(models.Model):
    """
    Publication model.
    """
    
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
    SuiviUtilisateur model.
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
        db_table = 'communaute_suivi_utilisateur'
        verbose_name = "Suivi d'utilisateur"
        verbose_name_plural = "Suivis d'utilisateurs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}"

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
