"""
Core models for the Django devstreet application.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from typing import List

from app.core.account_types import ACCOUNT_TYPE_CHOICES, ADMIN_ROLE_NAMES, TYPE_NONE



class Permission(models.Model):
    """
    Permission model for role-based access control.
    """
    code = models.CharField(max_length=100, unique=True, help_text="Unique permission code")
    description = models.TextField(blank=True, help_text="Description of the permission")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_permission'
        ordering = ['code']

    def __str__(self) -> str:
        return self.code


class Role(models.Model):
    """
    Role model for grouping permissions.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Unique role name")
    description = models.TextField(blank=True, help_text="Description of the role")
    permissions = models.ManyToManyField(
        Permission, 
        related_name='roles',
        blank=True,
        help_text="Permissions assigned to this role"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_role'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    def get_permissions(self) -> List[str]:
        """
        Get all permission codes for this role.
        
        Returns:
            List[str]: List of permission codes
        """
        return list(self.permissions.values_list('code', flat=True))


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    email = models.EmailField(unique=True, help_text="User's email address")
    first_name = models.CharField(max_length=150, help_text="User's first name")
    last_name = models.CharField(max_length=150, help_text="User's last name")
    photo = models.CharField(
        max_length=512,
        blank=True,
        default='',
        help_text="Chemin relatif de la photo de profil dans le stockage média",
    )
    banner = models.CharField(
        max_length=512,
        blank=True,
        default='',
        help_text="Chemin relatif de la bannière de profil dans le stockage média",
    )
    roles = models.ManyToManyField(
        Role, 
        related_name='users',
        blank=True,
        help_text="Roles assigned to this user"
    )
    is_active = models.BooleanField(default=True, help_text="Designates whether this user should be treated as active")
    account_type = models.CharField(
        max_length=12,
        choices=ACCOUNT_TYPE_CHOICES,
        blank=True,
        default=TYPE_NONE,
        help_text="Type de compte choisi à l'onboarding (vide tant que le membre n'a pas choisi)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'core_user'
        ordering = ['email']
        constraints = [
            # Un nom d'utilisateur désigne une seule personne, quelle que soit la casse
            models.UniqueConstraint(
                Lower('username'), name='core_user_username_ci_unique'
            ),
        ]

    def __str__(self) -> str:
        return self.email

    def has_permission(self, permission_code: str) -> bool:
        """
        Check if the user has a specific permission through their roles (superusers have all of them).
        
        Args:
            permission_code (str): The permission code to check
            
        Returns:
            bool: True if user has the permission, False otherwise
        """
        # Un superutilisateur actif a toutes les permissions (comme dans Django) ; les autres passent par leurs rôles
        if self.is_active and self.is_superuser:
            return True
        return self.roles.filter(permissions__code=permission_code).exists()

    def get_all_permissions(self) -> List[str]:
        """
        Get all permission codes for this user through their roles.
        
        Returns:
            List[str]: List of all permission codes
        """
        permissions = set()
        for role in self.roles.all():
            permissions.update(role.get_permissions())
        return list(permissions)

    def is_platform_admin(self) -> bool:
        """Vrai pour un superutilisateur ou un porteur d'un rôle IAM de base (administration de la plateforme)."""
        if self.is_superuser:
            return True
        return self.roles.filter(name__in=ADMIN_ROLE_NAMES).exists()

    def get_roles(self) -> List[str]:
        """
        Get all role names for this user.
        
        Returns:
            List[str]: List of role names
        """
        return list(self.roles.values_list('name', flat=True))

    @property
    def full_name(self) -> str:
        """
        Get the user's full name.
        
        Returns:
            str: Full name of the user
        """
        return f"{self.first_name} {self.last_name}".strip()


class PasswordResetChallenge(models.Model):
    """
    Challenge de réinitialisation de mot de passe (flux « mot de passe oublié »).

    Le code e-mail et le reset_token ne sont jamais stockés en clair :
    seules leurs empreintes HMAC-SHA256 le sont (voir forgot_password_service).
    """
    PURPOSE_RESET = 'reset'
    PURPOSE_CHANGE = 'change'
    PURPOSE_CHOICES = (
        (PURPOSE_RESET, 'Mot de passe oublié'),
        (PURPOSE_CHANGE, 'Changement de mot de passe (membre connecté)'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_challenges',
        help_text="Utilisateur qui a demandé la réinitialisation"
    )
    purpose = models.CharField(
        max_length=10,
        choices=PURPOSE_CHOICES,
        default=PURPOSE_RESET,
        help_text="Motif du code : un code de réinitialisation ne sert pas à un changement, et inversement",
    )
    code_hash = models.CharField(max_length=64, help_text="Empreinte HMAC du code envoyé par e-mail")
    expires_at = models.DateTimeField(help_text="Expiration du code")
    attempts = models.PositiveSmallIntegerField(default=0, help_text="Tentatives de saisie du code")
    code_used_at = models.DateTimeField(null=True, blank=True, help_text="Code consommé (étape 2 réussie)")
    reset_token_hash = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        unique=True,
        help_text="Empreinte HMAC du token à usage unique (après l'étape 2)"
    )
    token_expires_at = models.DateTimeField(null=True, blank=True, help_text="Expiration du token")
    token_used_at = models.DateTimeField(null=True, blank=True, help_text="Token consommé (étape 3 réussie)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_password_reset_challenge'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self) -> str:
        return f"Challenge #{self.pk} - {self.user_id}"


class AuditLog(models.Model):
    """
    Journal d'audit : qui a fait quoi, sur quoi, quand et depuis quelle adresse.

    Les entrées ne sont jamais modifiées (seule la purge planifiée les supprime). Les événements de connexion portent
    `subject` : l'empreinte SHA-256 de l'e-mail saisi, utilisée pour le verrouillage par compte sans stocker l'e-mail.
    `metadata` ne contient jamais de secret : noms de rôles, codes de permission, noms de champs modifiés.
    """
    actor = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_entries',
        help_text="Utilisateur à l'origine de l'action (vide pour une action anonyme ou un compte supprimé)"
    )
    action = models.CharField(max_length=60, db_index=True, help_text="Code de l'action, par exemple user.deleted")
    target_type = models.CharField(max_length=50, blank=True, help_text="Type d'objet concerné (user, role...)")
    target_id = models.CharField(max_length=64, blank=True, help_text="Identifiant de l'objet concerné")
    subject = models.CharField(max_length=64, blank=True, help_text="Empreinte SHA-256 de l'e-mail (événements de connexion)")
    ip_address = models.CharField(max_length=45, blank=True, help_text="Adresse du client (NUM_PROXIES fixe les proxys de confiance)")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'core_audit_log'
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['action', 'subject', '-created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.created_at:%Y-%m-%d %H:%M:%S} {self.action}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Une entrée du journal d'audit ne se modifie pas")
        super().save(*args, **kwargs)


class SocialAccount(models.Model):
    """
    Compte OAuth lié à un utilisateur DevStreet (Google, GitHub).
    Un même utilisateur peut avoir plusieurs providers ; un couple
    (provider, provider_user_id) n'appartient qu'à un seul compte.
    """

    PROVIDER_GOOGLE = 'google'
    PROVIDER_GITHUB = 'github'
    PROVIDER_CHOICES = (
        (PROVIDER_GOOGLE, 'Google'),
        (PROVIDER_GITHUB, 'GitHub'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_accounts',
        help_text="Utilisateur DevStreet lié à ce compte social",
    )
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        help_text="Fournisseur OAuth (google, github)",
    )
    provider_user_id = models.CharField(
        max_length=255,
        help_text="Identifiant stable chez le fournisseur",
    )
    email = models.EmailField(
        blank=True,
        default='',
        help_text="E-mail renvoyé par le fournisseur au moment de la liaison",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_social_account'
        ordering = ['provider', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'provider_user_id'],
                name='core_social_provider_uid_uniq',
            ),
        ]
        indexes = [
            models.Index(
                fields=['user', 'provider'],
                name='core_social_user_id_5f0e0c_idx',
            ),
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.provider_user_id} -> user {self.user_id}"
