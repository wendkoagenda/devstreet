"""
Serializers for the core application API.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from app.core.account_types import CHOOSABLE_TYPES
from app.core.models import Role, Permission
from app.core.username_rules import check_username

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Permission model.
    """
    role_count = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = ['id', 'code', 'description', 'role_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'role_count']

    def get_role_count(self, obj):
        """Get the number of roles that have this permission."""
        return obj.roles.count()

    def validate_code(self, value):
        """Validate permission code format."""
        if not value.replace('_', '').replace('.', '').isalnum():
            raise serializers.ValidationError(
                "Permission code can only contain letters, numbers, underscores, and dots"
            )
        return value


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role model.
    """
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_codes = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="List of permission codes to assign to this role"
    )
    user_count = serializers.SerializerMethodField()
    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'permissions', 'permission_codes',
            'user_count', 'permission_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'permissions', 'user_count', 'permission_count', 'created_at', 'updated_at']

    def get_user_count(self, obj):
        """Get the number of users assigned to this role."""
        return obj.users.count()

    def get_permission_count(self, obj):
        """Get the number of permissions assigned to this role."""
        return obj.permissions.count()


class RoleSimpleSerializer(serializers.ModelSerializer):
    """
    Simple serializer for Role model (for nested usage).
    """
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    roles = RoleSimpleSerializer(many=True, read_only=True)
    role_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="List of role names to assign to this user"
    )
    full_name = serializers.ReadOnlyField()
    permissions = serializers.SerializerMethodField()
    role_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'photo', 'banner', 'is_active', 'is_staff', 'is_superuser', 'roles',
            'role_names', 'permissions', 'role_count', 'date_joined', 'last_login',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'roles', 'full_name', 'photo', 'banner', 'permissions',
            'role_count', 'date_joined', 'last_login', 'created_at', 'updated_at'
        ]

    def get_permissions(self, obj):
        """Get all permissions for this user through their roles."""
        return obj.get_all_permissions()

    def get_role_count(self, obj):
        """Get the number of roles assigned to this user."""
        return obj.roles.count()

    def validate_email(self, value):
        """Validate email uniqueness."""
        if self.instance and self.instance.email == value:
            return value
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_username(self, value):
        """Valide le nom d'utilisateur : unique à la casse près et non réservé."""
        if self.instance and self.instance.username == value:
            return value

        error = check_username(
            value, exclude_pk=self.instance.pk if self.instance else None
        )
        if error:
            raise serializers.ValidationError(error)
        return value


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Modification, par le membre lui-même, de son identité : prénom, nom et nom d'utilisateur."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

    def validate_first_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Le prénom est obligatoire.")
        return value

    def validate_last_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Le nom est obligatoire.")
        return value

    def validate_username(self, value):
        """Unique à la casse près et non réservé ; le nom actuel reste valide."""
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Le nom d'utilisateur doit contenir au moins 3 caractères.")
        if self.instance and self.instance.username == value:
            return value
        error = check_username(value, exclude_pk=self.instance.pk if self.instance else None)
        if error:
            raise serializers.ValidationError(error)
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="List of role names to assign to this user"
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'role_names', 'is_active'
        ]

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_username(self, value):
        """Valide le nom d'utilisateur : unique à la casse près et non réservé."""
        error = check_username(value)
        if error:
            raise serializers.ValidationError(error)
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing users.
    """
    role_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="List of role names to assign to this user"
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'role_names', 'is_active', 'is_staff'
        ]

    def validate_email(self, value):
        """Validate email uniqueness."""
        if self.instance and self.instance.email == value:
            return value
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_username(self, value):
        """Valide le nom d'utilisateur : unique à la casse près et non réservé."""
        if self.instance and self.instance.username == value:
            return value

        error = check_username(
            value, exclude_pk=self.instance.pk if self.instance else None
        )
        if error:
            raise serializers.ValidationError(error)
        return value


class PublicRegisterSerializer(serializers.Serializer):
    """Inscription publique (sans attribution de rôles admin)."""

    email = serializers.EmailField()
    username = serializers.CharField(min_length=3, max_length=150)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {'password_confirm': 'Les mots de passe ne correspondent pas.'}
            )
        return attrs

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('Un compte existe déjà avec cet e-mail.')
        return email

    def validate_username(self, value):
        username = (value or '').strip()
        if not username:
            raise serializers.ValidationError("Le nom d'utilisateur est obligatoire.")
        if len(username) < 3:
            raise serializers.ValidationError(
                "Le nom d'utilisateur doit contenir au moins 3 caractères."
            )
        error = check_username(username)
        if error:
            raise serializers.ValidationError(error)
        return username


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)
    code = serializers.RegexField(
        regex=r'^\d{6}$',
        required=True,
        error_messages={
            'invalid': 'Le code doit contenir 6 chiffres.',
            'required': 'Saisissez le code reçu par e-mail.',
        },
    )

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match.")
        return attrs

    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class UserPermissionCheckSerializer(serializers.Serializer):
    """
    Serializer for checking user permissions.
    """
    permission_code = serializers.CharField(required=True)
    has_permission = serializers.BooleanField(read_only=True)


class RolePermissionSerializer(serializers.Serializer):
    """
    Serializer for managing role permissions.
    """
    permission_codes = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="List of permission codes to assign/remove"
    )


class UserRoleSerializer(serializers.Serializer):
    """
    Serializer for managing user roles.
    """
    role_names = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="List of role names to assign/remove"
    )


class BulkPermissionCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk creating permissions.
    """
    permissions = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text="List of permission objects to create"
    )

    def validate_permissions(self, value):
        """Validate permission data."""
        for permission_data in value:
            if 'code' not in permission_data:
                raise serializers.ValidationError("Each permission must have a 'code' field.")
            
            code = permission_data['code']
            if not code.replace('_', '').replace('.', '').isalnum():
                raise serializers.ValidationError(
                    f"Permission code '{code}' can only contain letters, numbers, underscores, and dots"
                )
        return value


class UserLoginSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    onboarding_required = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id", "email", "username", "first_name", "last_name", "full_name", "photo", "banner",
            "roles", "account_type", "is_admin", "onboarding_required",
        )
        read_only_fields = fields

    def get_roles(self, obj):
        return obj.get_roles() if hasattr(obj, 'get_roles') else []

    def get_is_admin(self, obj) -> bool:
        return obj.is_platform_admin()

    def get_onboarding_required(self, obj) -> bool:
        from app.core.services.account_type_service import AccountTypeService

        return AccountTypeService.onboarding_required(obj)


class AccountTypeSerializer(serializers.Serializer):
    """Choix du type de compte à l'onboarding (ou ajout d'un type plus tard)."""

    account_type = serializers.ChoiceField(choices=CHOOSABLE_TYPES)


class PublicProfileSerializer(serializers.ModelSerializer):
    """Profil public (mur) : identité visible sans e-mail ni rôles."""

    class Meta:
        model = User
        fields = ("id", "username", "full_name", "photo", "banner")
        read_only_fields = fields


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Étape 1 du « mot de passe oublié » : demande d'un code par e-mail.
    """
    email = serializers.EmailField(required=True)


class VerifyResetCodeSerializer(serializers.Serializer):
    """
    Étape 2 du « mot de passe oublié » : vérification du code reçu par e-mail.
    """
    email = serializers.EmailField(required=True)
    code = serializers.RegexField(
        regex=r'^\d{6}$',
        required=True,
        error_messages={'invalid': 'Le code doit contenir 6 chiffres.'}
    )


class ResetPasswordSerializer(serializers.Serializer):
    """
    Étape 3 du « mot de passe oublié » : nouveau mot de passe avec le reset_token.
    """
    reset_token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8, trim_whitespace=False)
    new_password_confirm = serializers.CharField(required=True, trim_whitespace=False)

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs
