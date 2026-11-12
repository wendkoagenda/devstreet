"""
ViewSet pour la gestion des rôles.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.core.models import Role
from app.core.serializers import RoleSerializer, RolePermissionSerializer
from app.core.services import audit_service
from app.core.services.audit_service import Actions
from app.core.services.role_service import RoleService
from app.core.views.mixins import AccessPolicyMixin
from app.core.permissions.user_permission import (
    CanViewRoles, CanCreateRoles, CanUpdateRoles, CanDeleteRoles
)


class RoleViewSet(AccessPolicyMixin, viewsets.ModelViewSet):
    swagger_tags = ['V1 - Role']
    """
    ViewSet pour les opérations CRUD sur les rôles.

    Fournit les actions standard : list, create, retrieve, update, destroy
    Plus des actions personnalisées pour la gestion des permissions.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    lookup_value_regex = '[0-9]+'  # un identifiant non numérique est une route inconnue (404), pas une erreur serveur

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_service = RoleService()

    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewRoles]
        elif self.action == 'create':
            permission_classes = [CanCreateRoles]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateRoles]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteRoles]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister tous les rôles",
        responses={200: RoleSerializer(many=True)},
        tags=['V1 - Role']
    )
    def list(self, request):
        """
        Retourne la liste de tous les rôles.
        """
        roles = self.role_service.get_all_roles()
        serializer = self.get_serializer(roles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouveau rôle",
        request_body=RoleSerializer,
        responses={
            201: RoleSerializer,
            400: "Données invalides"
        },
        tags=['V1 - Role']
    )
    def create(self, request):
        """
        Crée un nouveau rôle.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                permission_codes = list(serializer.validated_data.get('permission_codes', []))
                self.policy.ensure_can_grant_permissions(permission_codes)
                role = self.role_service.create_role(serializer.validated_data)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            audit_service.record(Actions.ROLE_CREATED, actor=request.user, target=role, target_label=role.name,
                                 request=request, metadata={'permissions': permission_codes})
            return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Récupérer un rôle par son ID",
        responses={
            200: RoleSerializer,
            404: "Rôle non trouvé"
        },
        tags=['V1 - Role']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'un rôle spécifique.
        """
        role = self.role_service.get_role_by_id(pk)
        if not role:
            return Response({'error': 'Rôle non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(role)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Mettre à jour un rôle",
        request_body=RoleSerializer,
        responses={
            200: RoleSerializer,
            400: "Données invalides",
            404: "Rôle non trouvé"
        },
        tags=['V1 - Role']
    )
    def update(self, request, pk=None):
        """
        Met à jour un rôle existant.
        """
        return self._apply_update(request, pk, partial=False)

    def _apply_update(self, request, pk, partial):
        role = self.role_service.get_role_by_id(pk)
        if not role:
            return Response({'error': 'Rôle non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(role, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = dict(serializer.validated_data)
        try:
            self.policy.ensure_can_modify_role(role)
            if 'permission_codes' in data:
                self.policy.ensure_can_grant_permissions(data['permission_codes'])
            updated = self.role_service.update_role(role.pk, dict(data))
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        metadata = {'fields': sorted(name for name in data if name != 'permission_codes')}
        if 'permission_codes' in data:
            metadata['permissions'] = list(data['permission_codes'])
        audit_service.record(Actions.ROLE_UPDATED, actor=request.user, target=updated, target_label=updated.name,
                             request=request, metadata=metadata)
        return Response(RoleSerializer(updated).data)

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un rôle",
        request_body=RoleSerializer,
        responses={
            200: RoleSerializer,
            400: "Données invalides",
            404: "Rôle non trouvé"
        },
        tags=['V1 - Role']
    )
    def partial_update(self, request, pk=None):
        return self._apply_update(request, pk, partial=True)

    @swagger_auto_schema(
        operation_description="Supprimer un rôle",
        responses={
            204: "Rôle supprimé avec succès",
            400: "Impossible de supprimer le rôle (utilisateurs assignés)",
            404: "Rôle non trouvé"
        },
        tags=['V1 - Role']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un rôle.
        """
        role = self.role_service.get_role_by_id(pk)
        if not role:
            return Response({'error': 'Rôle non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        self.policy.ensure_can_modify_role(role)
        role_id, name = role.pk, role.name
        try:
            self.role_service.delete_role(role_id)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        audit_service.record(Actions.ROLE_DELETED, actor=request.user, target_type='role', target_id=role_id,
                             target_label=name, request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(method='post', tags=['V1 - Role'])
    @action(detail=True, methods=['post'], permission_classes=[CanUpdateRoles])
    def assign_permission(self, request, pk=None):
        """
        Assigne une permission à un rôle.
        """
        permission_code = request.data.get('permission_code')
        if not permission_code:
            return Response({'error': 'Code de permission requis'}, status=status.HTTP_400_BAD_REQUEST)

        role = self.role_service.get_role_by_id(pk)
        if not role:
            return Response({'error': 'Rôle non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        self.policy.ensure_can_modify_role(role)
        self.policy.ensure_can_grant_permissions([permission_code])
        try:
            success = self.role_service.assign_permission_to_role(role.pk, permission_code)
            if success:
                audit_service.record(Actions.ROLE_PERMISSION_ASSIGNED, actor=request.user, target=role,
                                     target_label=role.name, request=request, metadata={'permissions': [permission_code]})
                return Response({'message': 'Permission assignée avec succès'})
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Échec de l\'assignation de la permission'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(method='post', tags=['V1 - Role'])
    @action(detail=True, methods=['post'], permission_classes=[CanUpdateRoles])
    def remove_permission(self, request, pk=None):
        """
        Retire une permission d'un rôle.
        """
        permission_code = request.data.get('permission_code')
        if not permission_code:
            return Response({'error': 'Code de permission requis'}, status=status.HTTP_400_BAD_REQUEST)

        role = self.role_service.get_role_by_id(pk)
        if not role:
            return Response({'error': 'Rôle non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        self.policy.ensure_can_modify_role(role)
        try:
            success = self.role_service.remove_permission_from_role(role.pk, permission_code)
            if success:
                audit_service.record(Actions.ROLE_PERMISSION_REMOVED, actor=request.user, target=role,
                                     target_label=role.name, request=request, metadata={'permissions': [permission_code]})
                return Response({'message': 'Permission retirée avec succès'})
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Échec du retrait de la permission'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(method='post', tags=['V1 - Role'])
    @action(detail=True, methods=['post'], permission_classes=[CanUpdateRoles])
    def bulk_assign_permissions(self, request, pk=None):
        """
        Assigne plusieurs permissions à un rôle en une seule opération.
        """
        serializer = RolePermissionSerializer(data=request.data)
        if serializer.is_valid():
            role = self.role_service.get_role_by_id(pk)
            if not role:
                return Response({'error': 'Rôle non trouvé'}, status=status.HTTP_404_NOT_FOUND)
            permission_codes = list(serializer.validated_data['permission_codes'])
            self.policy.ensure_can_modify_role(role)
            self.policy.ensure_can_grant_permissions(permission_codes)
            try:
                success = self.role_service.bulk_assign_permissions(role.pk, permission_codes)
                if success:
                    audit_service.record(Actions.ROLE_PERMISSIONS_BULK_ASSIGNED, actor=request.user, target=role,
                                         target_label=role.name, request=request, metadata={'permissions': permission_codes})
                    return Response({'message': 'Permissions assignées avec succès'})
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(method='get', tags=['V1 - Role'])
    @action(detail=True, methods=['get'], permission_classes=[CanViewRoles])
    def permissions(self, request, pk=None):
        """
        Retourne toutes les permissions d'un rôle.
        """
        permissions = self.role_service.get_role_permissions(pk)
        return Response({'permissions': permissions})

    @swagger_auto_schema(method='get', tags=['V1 - Role'])
    @action(detail=True, methods=['get'], permission_classes=[CanViewRoles])
    def user_count(self, request, pk=None):
        """
        Retourne le nombre d'utilisateurs assignés à un rôle.
        """
        count = self.role_service.get_role_user_count(pk)
        return Response({'user_count': count})

    @swagger_auto_schema(method='get', tags=['V1 - Role'])
    @action(detail=False, methods=['get'], permission_classes=[CanViewRoles])
    def search(self, request):
        """
        Recherche des rôles par nom ou description.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Paramètre de recherche requis'}, status=status.HTTP_400_BAD_REQUEST)

        roles = self.role_service.search_roles(query)
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(method='get', tags=['V1 - Role'])
    @action(detail=False, methods=['get'], permission_classes=[CanViewRoles])
    def with_permission(self, request):
        """
        Retourne les rôles qui ont une permission spécifique.
        """
        permission_code = request.query_params.get('permission_code')
        if not permission_code:
            return Response({'error': 'Code de permission requis'}, status=status.HTTP_400_BAD_REQUEST)

        roles = self.role_service.get_roles_with_permission(permission_code)
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)