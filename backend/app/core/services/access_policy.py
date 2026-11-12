"""
Politique d'accès aux comptes et aux rôles : qui peut modifier qui, et attribuer quoi.

Avoir la permission `users.update` ou `roles.update` ne suffit pas : sans règle de hiérarchie, un gestionnaire pourrait
se donner à lui-même (ou donner à un complice) le rôle Super Admin. Les règles :

- on n'attribue qu'un rôle ou une permission que l'on possède soi-même (aucune montée en puissance) ;
- on ne gère pas un compte, ni un rôle, plus puissant que le sien ;
- seul un superutilisateur gère un superutilisateur ou modifie `is_staff` ;
- on ne modifie pas ses propres rôles ni ses propres droits, on ne supprime pas son propre compte ;
- le dernier superutilisateur actif ne peut être ni supprimé ni désactivé (sinon plus personne n'administre).

Un superutilisateur actif n'est pas soumis à la hiérarchie, sauf pour les règles sur soi-même et le dernier superutilisateur.
Les services restent utilisables sans acteur par les seeds et les commandes : cette politique est appelée par les vues.
"""
from typing import Any, Dict, Iterable, Set

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from app.core.repositories.role_repository import RoleRepository

User = get_user_model()


class AccessDenied(Exception):
    """Action refusée par la politique d'accès. Le message est destiné à l'utilisateur."""


class AccessPolicy:
    def __init__(self, actor):
        self.actor = actor
        self.role_repository = RoleRepository()
        self._permissions: Set[str] = set()
        self._loaded = False

    # ------------------------------------------------------------------ outils
    def _is_superuser(self) -> bool:
        return bool(self.actor.is_active and self.actor.is_superuser)

    def _own_permissions(self) -> Set[str]:
        if not self._loaded:
            self._permissions, self._loaded = set(self.actor.get_all_permissions()), True
        return self._permissions

    def _holds_all(self, codes: Iterable[str]) -> bool:
        return self._is_superuser() or set(codes) <= self._own_permissions()

    def _is_self(self, target) -> bool:
        return target.pk == self.actor.pk

    # ------------------------------------------------------------------ rôles et permissions
    def ensure_can_grant_permissions(self, codes: Iterable[str]) -> None:
        if not self._holds_all(codes):
            raise AccessDenied("Vous ne pouvez attribuer que des permissions que vous possédez vous-même.")

    def ensure_can_modify_role(self, role) -> None:
        if not self._holds_all(role.get_permissions()):
            raise AccessDenied("Ce rôle est plus puissant que le vôtre : vous ne pouvez pas le modifier.")

    def ensure_can_grant_roles(self, role_names: Iterable[str]) -> None:
        for name in role_names:
            role = self.role_repository.get_by_name(name)
            if not role:
                raise ValidationError(f"Role '{name}' does not exist")
            if not self._holds_all(role.get_permissions()):
                raise AccessDenied("Vous ne pouvez pas attribuer un rôle plus puissant que le vôtre.")

    # ------------------------------------------------------------------ comptes
    def ensure_can_manage_user(self, target) -> None:
        """Modifier, supprimer ou changer les rôles d'un AUTRE compte."""
        if self._is_self(target):
            raise AccessDenied("Cette action est impossible sur votre propre compte.")
        if self._is_superuser():
            return
        if target.is_superuser:
            raise AccessDenied("Seul un superutilisateur peut gérer un superutilisateur.")
        if not self._holds_all(target.get_all_permissions()):
            raise AccessDenied("Ce compte a des droits supérieurs aux vôtres : vous ne pouvez pas le gérer.")

    def ensure_not_last_superuser(self, target) -> None:
        others = User.objects.filter(is_superuser=True, is_active=True).exclude(pk=target.pk)
        if target.is_superuser and target.is_active and not others.exists():
            raise AccessDenied("Opération impossible : c'est le dernier superutilisateur actif.")

    def ensure_can_create_user(self, role_names: Iterable[str]) -> None:
        self.ensure_can_grant_roles(role_names)

    def ensure_can_update_user(self, target, data: Dict[str, Any]) -> None:
        """`data` : champs validés de la mise à jour (role_names, is_staff, is_active, profil)."""
        roles_changed = 'role_names' in data and set(data['role_names']) != set(target.get_roles())
        staff_changed = 'is_staff' in data and data['is_staff'] != target.is_staff
        active_changed = 'is_active' in data and data['is_active'] != target.is_active

        if self._is_self(target):
            if roles_changed or staff_changed or active_changed:
                raise AccessDenied("Vous ne pouvez pas modifier vos propres rôles ni vos propres droits.")
            return
        self.ensure_can_manage_user(target)
        if staff_changed and not self._is_superuser():
            raise AccessDenied("Seul un superutilisateur peut modifier le droit d'accès à l'administration (is_staff).")
        if roles_changed:
            self.ensure_can_grant_roles(data['role_names'])
        if active_changed and not data['is_active']:
            self.ensure_not_last_superuser(target)

    def ensure_can_delete_user(self, target) -> None:
        if self._is_self(target):
            raise AccessDenied("Vous ne pouvez pas supprimer votre propre compte.")
        self.ensure_can_manage_user(target)
        self.ensure_not_last_superuser(target)

    def ensure_can_assign_role(self, target, role_name: str) -> None:
        self.ensure_can_manage_user(target)
        self.ensure_can_grant_roles([role_name])

    def ensure_can_remove_role(self, target) -> None:
        self.ensure_can_manage_user(target)
