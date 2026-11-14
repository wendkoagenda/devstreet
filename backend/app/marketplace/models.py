from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class Company(models.Model):
    """
    Company model.
    """
    
    name = models.CharField(help_text="Nom de l'entreprise", max_length=150)
    slug = models.SlugField(help_text='URL publique', max_length=160, unique=True)
    logo = models.CharField(help_text='Logo, stocké en stockage objet', max_length=512, blank=True, default='')
    description = models.TextField(help_text="Présentation de l'entreprise", blank=True, default='')
    sector = models.CharField(help_text="Secteur d'activité", max_length=30, choices=[('fintech', 'Fintech'), ('ecommerce', 'E-commerce'), ('agritech', 'Agritech'), ('edtech', 'Edtech'), ('health', 'Santé'), ('ngo', 'ONG'), ('public', 'Secteur public'), ('other', 'Autre')])
    size = models.CharField(help_text="Taille de l'entreprise", max_length=10, blank=True, default='', choices=[('1-10', '1-10'), ('11-50', '11-50'), ('51-200', '51-200'), ('200+', '200+')])
    website = models.URLField(help_text='Site web', blank=True, default='')
    contact_email = models.EmailField(help_text='E-mail de contact', blank=True, default='')
    phone = models.CharField(help_text='Téléphone', max_length=20, blank=True, default='')
    country = models.CharField(help_text='Code pays ISO 3166-1 (ex. BF, SN)', max_length=2)
    city = models.CharField(help_text='Ville', max_length=100, blank=True, default='')
    address = models.CharField(help_text='Adresse', max_length=255, blank=True, default='')
    is_verified = models.BooleanField(help_text="Vérifiée par l'admin", default=False)
    verified_at = models.DateTimeField(help_text='Date de vérification', blank=True, null=True)
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
        db_table = 'marketplace_company'
        verbose_name = 'Entreprise'
        verbose_name_plural = 'Entreprises'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return f"/marketplace/companies/{self.id}/"


class Skill(models.Model):
    """
    Skill model.
    """
    
    name = models.CharField(help_text='Nom (ex. « Django »)', max_length=80, unique=True)
    slug = models.SlugField(help_text='Identifiant URL', max_length=90, unique=True)
    type = models.CharField(help_text='Compétence technique ou comportementale', max_length=4, choices=[('hard', 'Technique'), ('soft', 'Comportementale')])
    category = models.CharField(help_text='Famille de compétences', max_length=20, blank=True, default='', choices=[('frontend', 'Frontend'), ('backend', 'Backend'), ('mobile', 'Mobile'), ('devops', 'DevOps'), ('data', 'Data'), ('design', 'Design'), ('management', 'Management'), ('soft', 'Comportementale')])
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
        db_table = 'marketplace_skill'
        verbose_name = 'Compétence'
        verbose_name_plural = 'Compétences'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return f"/marketplace/skills/{self.id}/"


class Profil(models.Model):
    """
    Profil model.

    Un membre peut avoir un profil `dev` et un profil `entreprise` (au plus un de chaque type).
    Le profil `entreprise` est toujours rattaché à une entreprise ; le profil `dev` n'en a pas.
    """

    TYPE_DEV = 'dev'
    TYPE_ENTREPRISE = 'entreprise'
    TYPE_CHOICES = [(TYPE_DEV, 'Dev'), (TYPE_ENTREPRISE, 'Entreprise')]

    type = models.CharField(help_text="Profil de développeur ou profil d'entreprise", max_length=10, choices=TYPE_CHOICES, default=TYPE_DEV)
    is_company_owner = models.BooleanField(help_text="Propriétaire de l'entreprise rattachée", default=False)
    slug = models.SlugField(help_text='URL publique du profil', max_length=160, unique=True)
    photo = models.CharField(help_text='Photo, affichée sur le CV', max_length=512, blank=True, default='')
    headline = models.CharField(help_text='Accroche (ex. « Dev React, 5 ans »)', max_length=160, blank=True, default='')
    bio = models.TextField(help_text='Résumé, utilisé en tête du CV', blank=True, default='')
    phone = models.CharField(help_text='Téléphone', max_length=20, blank=True, default='')
    country = models.CharField(help_text='Code pays ISO 3166-1', max_length=2)
    city = models.CharField(help_text='Ville', max_length=100, blank=True, default='')
    remote = models.BooleanField(help_text='Accepte le télétravail', default=True)
    timezone = models.CharField(help_text='Fuseau horaire IANA (ex. Africa/Ouagadougou)', max_length=50, default='UTC')
    default_hours_per_week = models.PositiveSmallIntegerField(help_text='Capacité hebdomadaire par défaut, hors périodes du calendrier', default=40)
    is_open_to_work = models.BooleanField(help_text="Visible dans l'annuaire et les recommandations", default=True)
    daily_rate = models.DecimalField(help_text='Tarif journalier indicatif', blank=True, null=True, max_digits=12, decimal_places=2)
    currency = models.CharField(help_text='Devise ISO 4217', max_length=3, default='XOF')
    years_of_experience = models.PositiveSmallIntegerField(help_text="Années d'expérience", default=0)
    languages = models.JSONField(help_text='Langues parlées, ex. [{"language": "fr", "level": "native"}]', blank=True, default=list)
    github_url = models.URLField(help_text='Profil GitHub', blank=True, default='')
    linkedin_url = models.URLField(help_text='Profil LinkedIn', blank=True, default='')
    portfolio_url = models.URLField(help_text='Portfolio', blank=True, default='')
    cv_visibility = models.CharField(help_text='Qui peut télécharger le CV', max_length=10, default='companies', choices=[('public', 'Public'), ('companies', 'Entreprises'), ('private', 'Privé')])
    cv_settings = models.JSONField(help_text='Réglages de style du CV (couleur, police, mise en page…)', blank=True, default=dict)
    embedding = models.JSONField(help_text="Vecteur pour le matching IA (pgvector), dimension selon le modèle d'embeddings retenu (JSON provisoire, futur VectorField pgvector)", blank=True, null=True)
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
    company = models.ForeignKey('marketplace.Company', on_delete=models.SET_NULL, related_name='profils', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='marketplace_profils')
    skills = models.ManyToManyField('marketplace.Skill', through='marketplace.ProfilSkill', related_name='profils')


    class Meta:
        db_table = 'marketplace_profil'
        verbose_name = 'Profil'
        verbose_name_plural = 'Profils'
        ordering = ['-created_at']
        constraints = [
            # Au plus un profil de chaque type par membre
            models.UniqueConstraint(fields=['user', 'type'], name='uniq_profil_user_type'),
            # Profil entreprise : entreprise obligatoire ; profil dev : jamais d'entreprise
            models.CheckConstraint(
                condition=(
                    (models.Q(type='entreprise') & models.Q(company__isnull=False))
                    | (models.Q(type='dev') & models.Q(company__isnull=True))
                ),
                name='profil_type_company_coherent',
            ),
        ]

    def __str__(self):
        return f"{self.headline}"

    def get_absolute_url(self):
        return f"/marketplace/profils/{self.id}/"


class ProfilTypeRulesMixin:
    """
    Vérifie que chaque relation vers un profil pointe vers le bon type (dev ou entreprise).

    Les modèles déclarent `PROFIL_TYPE_RULES` : nom du champ -> type attendu. Un modèle dont la règle dépend
    de ses données (ex. le swipe, selon son contexte) redéfinit `profil_type_rules()`.
    Le contrôle s'applique à toute écriture (administration, services, scripts).
    """

    PROFIL_TYPE_RULES = {}

    def profil_type_rules(self):
        return self.PROFIL_TYPE_RULES

    def check_profil_types(self):
        from django.core.exceptions import ValidationError

        for field, expected in self.profil_type_rules().items():
            profil_id = getattr(self, f'{field}_id', None)
            if profil_id is None:
                continue
            actual = Profil.objects.filter(pk=profil_id).values_list('type', flat=True).first()
            if actual is not None and actual != expected:
                label = 'dev' if expected == Profil.TYPE_DEV else 'entreprise'
                raise ValidationError({field: f"Un profil {label} est attendu pour ce champ."})

    def save(self, *args, **kwargs):
        self.check_profil_types()
        super().save(*args, **kwargs)


class Offer(ProfilTypeRulesMixin, models.Model):
    """
    Offer model.
    """

    PROFIL_TYPE_RULES = {'recruiter': 'entreprise'}
    
    title = models.CharField(help_text="Titre de l'offre", max_length=200)
    slug = models.SlugField(help_text='URL publique', max_length=220, unique=True)
    description = models.TextField(help_text="Description, peut être générée par l'IA")
    type = models.CharField(help_text='Type de contrat', max_length=10, choices=[('mission', 'Mission'), ('cdd', 'CDD'), ('cdi', 'CDI'), ('stage', 'Stage')])
    contract_duration = models.PositiveSmallIntegerField(help_text="Durée (mission, CDD, stage), exprimée dans l'unité `contract_duration_unit`", blank=True, null=True)
    contract_duration_unit = models.CharField(help_text='Unité de la durée : heures, jours, mois ou années', max_length=5, default='month', choices=[('hour', 'Heures'), ('day', 'Jours'), ('month', 'Mois'), ('year', 'Années')])
    experience_level = models.CharField(help_text='Niveau attendu', max_length=10, choices=[('junior', 'Junior'), ('mid', 'Intermédiaire'), ('senior', 'Senior'), ('expert', 'Expert')])
    budget_min = models.DecimalField(help_text='Budget ou salaire minimum', blank=True, null=True, max_digits=12, decimal_places=2)
    budget_max = models.DecimalField(help_text='Budget ou salaire maximum', blank=True, null=True, max_digits=12, decimal_places=2)
    currency = models.CharField(help_text='Devise ISO 4217', max_length=3, default='XOF')
    budget_period = models.CharField(help_text='Période du budget', max_length=10, default='month', choices=[('day', 'Par jour'), ('month', 'Par mois'), ('fixed', 'Forfait')])
    country = models.CharField(help_text='Code pays ISO 3166-1', max_length=2)
    city = models.CharField(help_text='Ville', max_length=100, blank=True, default='')
    work_mode = models.CharField(help_text='Mode de travail', max_length=10, default='on_site', choices=[('on_site', 'Sur site'), ('hybrid', 'Hybride'), ('remote', 'À distance')])
    start_date = models.DateField(help_text='Date de démarrage souhaitée', blank=True, null=True)
    deadline = models.DateField(help_text='Date limite de candidature', blank=True, null=True)
    status = models.CharField(help_text="Statut de l'offre", max_length=10, default='draft', choices=[('draft', 'Brouillon'), ('open', 'Ouverte'), ('closed', 'Clôturée')])
    published_at = models.DateTimeField(help_text='Date de publication', blank=True, null=True)
    views_count = models.PositiveIntegerField(help_text='Nombre de vues', default=0)
    embedding = models.JSONField(help_text='Vecteur pour le matching IA (pgvector) (JSON provisoire, futur VectorField pgvector)', blank=True, null=True)
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
    company = models.ForeignKey('marketplace.Company', on_delete=models.RESTRICT, related_name='offers')
    recruiter = models.ForeignKey('marketplace.Profil', on_delete=models.RESTRICT, related_name='created_offers')
    required_skills = models.ManyToManyField('marketplace.Skill', related_name='offers')
    candidates = models.ManyToManyField('marketplace.Profil', through='marketplace.Candidature', related_name='applied_offers')




    class Meta:
        db_table = 'marketplace_offer'
        verbose_name = 'Offre'
        verbose_name_plural = 'Offres'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return f"/marketplace/offers/{self.id}/"


class Candidature(ProfilTypeRulesMixin, models.Model):
    """
    Candidature model.
    """

    PROFIL_TYPE_RULES = {'profil': 'dev'}
    
    message = models.TextField(help_text='Message de motivation', blank=True, default='')
    status = models.CharField(help_text='Statut de la candidature', max_length=15, default='sent', choices=[('sent', 'Envoyée'), ('shortlisted', 'Présélectionnée'), ('rejected', 'Refusée'), ('accepted', 'Acceptée')])
    ai_match_score = models.DecimalField(help_text='Score du moteur de recommandation, de 0 à 100', blank=True, null=True, max_digits=5, decimal_places=2)
    cv_snapshot = models.CharField(help_text='CV PDF figé au moment de la candidature', max_length=512, blank=True, default='')
    decided_at = models.DateTimeField(help_text="Date de la décision de l'entreprise", blank=True, null=True)
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
    offer = models.ForeignKey('marketplace.Offer', on_delete=models.CASCADE, related_name='candidatures')
    profil = models.ForeignKey('marketplace.Profil', on_delete=models.CASCADE, related_name='candidatures')



    class Meta:
        db_table = 'marketplace_candidature'
        verbose_name = 'Candidature'
        verbose_name_plural = 'Candidatures'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['offer', 'profil'], name='uniq_candidature_offer_profil'),
        ]

    def __str__(self):
        return f"{self.status}"

    def get_absolute_url(self):
        return f"/marketplace/candidatures/{self.id}/"


class ProfilSkill(ProfilTypeRulesMixin, models.Model):
    """
    ProfilSkill model.
    """

    PROFIL_TYPE_RULES = {'profil': 'dev'}
    
    level = models.PositiveSmallIntegerField(help_text='Niveau déclaré, de 1 à 5', validators=[MinValueValidator(1), MaxValueValidator(5)])
    years = models.PositiveSmallIntegerField(help_text='Années de pratique', default=0)
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
    profil = models.ForeignKey('marketplace.Profil', on_delete=models.CASCADE, related_name='profil_skills')
    skill = models.ForeignKey('marketplace.Skill', on_delete=models.CASCADE, related_name='profil_skills')



    class Meta:
        db_table = 'marketplace_profil_skill'
        verbose_name = 'Compétence du profil'
        verbose_name_plural = 'Compétences du profil'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['profil', 'skill'], name='uniq_profil_skill'),
        ]

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return f"/marketplace/profil-skills/{self.id}/"


class Experience(ProfilTypeRulesMixin, models.Model):
    """
    Experience model.
    """

    PROFIL_TYPE_RULES = {'profil': 'dev'}
    
    title = models.CharField(help_text='Poste occupé', max_length=150)
    company_name = models.CharField(help_text='Employeur ou client', max_length=150)
    location = models.CharField(help_text='Ville, pays ou remote', max_length=150, blank=True, default='')
    contract_type = models.CharField(help_text='Type de contrat', max_length=15, blank=True, default='', choices=[('cdi', 'CDI'), ('cdd', 'CDD'), ('freelance', 'Freelance'), ('stage', 'Stage')])
    start_date = models.DateField(help_text='Date de début')
    end_date = models.DateField(help_text='Date de fin, vide si poste actuel', blank=True, null=True)
    is_current = models.BooleanField(help_text='Poste actuel', default=False)
    description = models.TextField(help_text='Missions et réalisations', blank=True, default='')
    technologies = models.CharField(help_text='Stack utilisée', max_length=255, blank=True, default='')
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
    profil = models.ForeignKey('marketplace.Profil', on_delete=models.CASCADE, related_name='experiences')


    class Meta:
        db_table = 'marketplace_experience'
        verbose_name = 'Expérience'
        verbose_name_plural = 'Expériences'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return f"/marketplace/experiences/{self.id}/"


class Prestation(ProfilTypeRulesMixin, models.Model):
    """
    Prestation model.
    """

    PROFIL_TYPE_RULES = {'profil': 'dev'}
    
    title = models.CharField(help_text='Titre de la prestation', max_length=150)
    slug = models.SlugField(help_text='URL publique', max_length=160, unique=True)
    description = models.TextField(help_text='Contenu de la prestation')
    category = models.CharField(help_text='Catégorie', max_length=20, choices=[('web', 'Web'), ('mobile', 'Mobile'), ('design', 'Design'), ('devops', 'DevOps'), ('data', 'Data'), ('other', 'Autre')])
    price = models.DecimalField(help_text='Prix fixe', max_digits=12, decimal_places=2)
    currency = models.CharField(help_text='Devise ISO 4217', max_length=3, default='XOF')
    delivery_days = models.PositiveSmallIntegerField(help_text='Délai de livraison en jours')
    revisions = models.PositiveSmallIntegerField(help_text='Nombre de retouches incluses', default=1)
    cover_image = models.CharField(help_text='Visuel de présentation', max_length=512, blank=True, default='')
    is_active = models.BooleanField(help_text='Visible sur la marketplace', default=True)
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
    profil = models.ForeignKey('marketplace.Profil', on_delete=models.CASCADE, related_name='prestations')


    class Meta:
        db_table = 'marketplace_prestation'
        verbose_name = 'Prestation'
        verbose_name_plural = 'Prestations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return f"/marketplace/prestations/{self.id}/"


class ProfilHistory(ProfilTypeRulesMixin, models.Model):
    """
    ProfilHistory model.
    """

    PROFIL_TYPE_RULES = {'profil': 'dev'}
    
    field = models.CharField(help_text='Nom du champ modifié', max_length=100)
    old_value = models.TextField(help_text='Valeur avant modification', blank=True, default='')
    new_value = models.TextField(help_text='Valeur après modification', blank=True, default='')
    source = models.CharField(help_text='Origine de la modification', max_length=10, default='manual', choices=[('manual', 'Saisie manuelle'), ('ai', 'IA'), ('system', 'Système')])
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
    profil = models.ForeignKey('marketplace.Profil', on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='marketplace_profil_changes', null=True, blank=True)


    class Meta:
        db_table = 'marketplace_profil_history'
        verbose_name = 'Historique de profil'
        verbose_name_plural = 'Historiques de profil'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.field}"

    def get_absolute_url(self):
        return f"/marketplace/profil-histories/{self.id}/"


class Availability(ProfilTypeRulesMixin, models.Model):
    """
    Availability model.
    """

    PROFIL_TYPE_RULES = {'profil': 'dev'}
    
    start_date = models.DateField(help_text='Début de la période')
    end_date = models.DateField(help_text='Fin de la période (incluse)')
    status = models.CharField(help_text='Disponible, partiel, occupé ou congé', max_length=10, choices=[('available', 'Disponible'), ('partial', 'Partiel'), ('busy', 'Occupé'), ('leave', 'Congé')])
    hours_per_week = models.PositiveSmallIntegerField(help_text='Capacité sur la période (utile pour le statut partial)', blank=True, null=True)
    source = models.CharField(help_text='Saisie manuelle ou créée par une candidature acceptée', max_length=10, default='manual', choices=[('manual', 'Saisie manuelle'), ('mission', 'Mission')])
    note = models.CharField(help_text='Commentaire libre', max_length=255, blank=True, default='')
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
    profil = models.ForeignKey('marketplace.Profil', on_delete=models.CASCADE, related_name='availabilities')


    class Meta:
        db_table = 'marketplace_availability'
        verbose_name = 'Disponibilité'
        verbose_name_plural = 'Disponibilités'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.status}"

    def get_absolute_url(self):
        return f"/marketplace/availabilities/{self.id}/"


class Review(ProfilTypeRulesMixin, models.Model):
    """
    Review model.
    """

    PROFIL_TYPE_RULES = {'target': 'dev', 'author': 'dev'}
    
    rating = models.PositiveSmallIntegerField(help_text='Note de 1 à 5', validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(help_text='Commentaire', blank=True, default='')
    is_public = models.BooleanField(help_text='Affiché sur le profil et le CV', default=True)
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
    target = models.ForeignKey('marketplace.Profil', on_delete=models.CASCADE, related_name='reviews_received')
    author = models.ForeignKey('marketplace.Profil', on_delete=models.CASCADE, related_name='reviews_given')
    candidature = models.ForeignKey('marketplace.Candidature', on_delete=models.SET_NULL, related_name='reviews', null=True, blank=True)




    class Meta:
        db_table = 'marketplace_review'
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}"

    def get_absolute_url(self):
        return f"/marketplace/reviews/{self.id}/"


class Swipe(ProfilTypeRulesMixin, models.Model):
    """
    Swipe model.
    """

    PROFIL_TYPE_RULES = {}
    
    direction = models.CharField(help_text='Swipe à droite (like) ou à gauche (pass)', max_length=4, choices=[('like', 'Like'), ('pass', 'Passer')])
    context = models.CharField(help_text='Recrutement (entreprise vers dev) ou réseau (dev vers dev)', max_length=10, choices=[('recruit', 'Recrutement'), ('network', 'Réseau')])
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
    author = models.ForeignKey('marketplace.Profil', on_delete=models.CASCADE, related_name='swipes_given')
    target = models.ForeignKey('marketplace.Profil', on_delete=models.CASCADE, related_name='swipes_received')



    class Meta:
        db_table = 'marketplace_swipe'
        verbose_name = 'Swipe'
        verbose_name_plural = 'Swipes'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['author', 'target', 'context'], name='uniq_swipe_author_target_context'),
        ]

    def profil_type_rules(self):
        """Recrutement : entreprise vers dev. Réseau : tout profil (dev ou entreprise) vers tout profil."""
        if self.context == 'recruit':
            return {'author': 'entreprise', 'target': 'dev'}
        return {}

    def __str__(self):
        return f"{self.direction}"

    def get_absolute_url(self):
        return f"/marketplace/swipes/{self.id}/"


class Connection(ProfilTypeRulesMixin, models.Model):
    """
    Connection model.
    """

    # Le réseau est général : un profil dev ou entreprise peut se connecter à n'importe quel autre profil
    PROFIL_TYPE_RULES = {}
    
    status = models.CharField(help_text='Connexion active ou bloquée', max_length=10, default='matched', choices=[('matched', 'Connectés'), ('blocked', 'Bloquée')])
    matched_at = models.DateTimeField(help_text='Date du like mutuel')
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
    profil_a = models.ForeignKey('marketplace.Profil', on_delete=models.CASCADE, related_name='connections_as_a')
    profil_b = models.ForeignKey('marketplace.Profil', on_delete=models.CASCADE, related_name='connections_as_b')



    class Meta:
        db_table = 'marketplace_connection'
        verbose_name = 'Connexion'
        verbose_name_plural = 'Connexions'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['profil_a', 'profil_b'], name='uniq_connection_a_b'),
        ]

    def __str__(self):
        return f"{self.status}"

    def get_absolute_url(self):
        return f"/marketplace/connections/{self.id}/" 


class InvitationEntreprise(models.Model):
    """
    Invitation à rejoindre une entreprise : à usage unique, révocable, avec expiration.

    Seul le hash du jeton est conservé ; le lien complet n'est montré qu'à la création.
    """

    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REVOKED = 'revoked'
    STATUS_CHOICES = [(STATUS_PENDING, 'En attente'), (STATUS_ACCEPTED, 'Acceptée'), (STATUS_REVOKED, 'Révoquée')]

    company = models.ForeignKey('marketplace.Company', on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='entreprise_invitations_sent', null=True, blank=True)
    email = models.EmailField(help_text="Adresse de la personne invitée (facultative : le lien peut être partagé)", blank=True, default='')
    token_hash = models.CharField(help_text='Hash du jeton du lien', max_length=64, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    expires_at = models.DateTimeField(help_text="Date d'expiration du lien")
    accepted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='entreprise_invitations_accepted', null=True, blank=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'marketplace_invitation_entreprise'
        verbose_name = "Invitation d'entreprise"
        verbose_name_plural = "Invitations d'entreprise"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company_id} · {self.status}"
