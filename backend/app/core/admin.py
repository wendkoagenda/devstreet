"""
Django admin configuration for core models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from app.core.models import AuditLog, User, Role, Permission, PasswordResetChallenge


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Permission model.
    """
    list_display = ('code', 'description', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('code', 'description')
    ordering = ('code',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin configuration for Role model.
    """
    list_display = ('name', 'description', 'get_permissions_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('permissions',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    def get_permissions_count(self, obj):
        """Get the number of permissions for this role."""
        return obj.permissions.count()
    get_permissions_count.short_description = 'Permissions Count'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for User model.
    """
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_roles_count')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'roles')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions', 'roles')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Roles'), {'fields': ('roles',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    def get_roles_count(self, obj):
        """Get the number of roles for this user."""
        return obj.roles.count()
    get_roles_count.short_description = 'Roles Count'


@admin.register(PasswordResetChallenge)
class PasswordResetChallengeAdmin(admin.ModelAdmin):
    """
    Admin (lecture seule) des challenges de réinitialisation de mot de passe.
    Les empreintes ne sont volontairement pas affichées.
    """
    list_display = ('id', 'user', 'attempts', 'expires_at', 'code_used_at', 'token_expires_at', 'token_used_at', 'created_at')
    list_filter = ('created_at', 'code_used_at', 'token_used_at')
    search_fields = ('user__email',)
    ordering = ('-created_at',)
    exclude = ('code_hash', 'reset_token_hash')
    readonly_fields = ('user', 'attempts', 'expires_at', 'code_used_at', 'token_expires_at', 'token_used_at', 'created_at')

    def has_add_permission(self, request):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Journal d'audit en lecture seule : aucune entrée ne s'ajoute, ne se modifie ni ne se supprime depuis l'admin.
    """
    list_display = ('created_at', 'action', 'actor', 'target_type', 'target_id', 'ip_address')
    list_filter = ('action', 'target_type')
    search_fields = ('action', 'target_id', 'subject')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
