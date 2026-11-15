"""Service du type de compte : choix à l'onboarding, ajout d'un type, rôles associés."""
from django.db import transaction

from app.core.account_types import (
    ROLE_DESCRIPTIONS,
    TYPE_NONE,
    merge_account_type,
    permission_codes_for_role,
    role_names_for,
    split_types,
)
from app.core.models import Permission, Role


class AccountTypeService:
    """Applique un type de compte à un utilisateur et lui attribue les rôles correspondants."""

    @staticmethod
    def ensure_role(role_name: str) -> Role:
        """Crée le rôle de membre (et complète ses permissions) s'il manque."""
        role, _ = Role.objects.get_or_create(
            name=role_name,
            defaults={'description': ROLE_DESCRIPTIONS.get(role_name, '')},
        )
        needed = permission_codes_for_role(role_name)
        missing = needed - set(role.permissions.values_list('code', flat=True))
        if missing:
            perms = [
                Permission.objects.get_or_create(
                    code=code, defaults={'description': f'Permission {code}'}
                )[0]
                for code in sorted(missing)
            ]
            role.permissions.add(*perms)
        return role

    @classmethod
    @transaction.atomic
    def add_type(cls, user, requested: str):
        """
        Ajoute le type demandé au compte (jamais de retrait) et attribue les rôles manquants.

        Un type déjà porté est ignoré ; l'appel est donc idempotent.
        """
        merged = merge_account_type(user.account_type, requested)
        if merged == TYPE_NONE:
            return user
        if merged != user.account_type:
            user.account_type = merged
            user.save(update_fields=['account_type', 'updated_at'])
        for role_name in role_names_for(merged):
            user.roles.add(cls.ensure_role(role_name))
        return user

    @staticmethod
    def onboarding_required(user) -> bool:
        """Vrai si le membre doit passer par l'assistant : pas d'administrateur, pas de type choisi."""
        return not split_types(user.account_type) and not user.is_platform_admin()
