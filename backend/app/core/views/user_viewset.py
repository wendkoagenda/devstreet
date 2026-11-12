"""
ViewSet pour la gestion des utilisateurs.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.core.serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    UserRoleSerializer, UserPermissionCheckSerializer
)
from app.core.services import audit_service
from app.core.services.audit_service import Actions
from app.core.services.user_service import UserService
from app.core.permissions.user_permission import (
    CanViewUsers, CanCreateUsers, CanUpdateUsers, CanDeleteUsers
)
from app.core.views.mixins import AccessPolicyMixin

User = get_user_model()

NOT_FOUND_MESSAGE = 'Utilisateur non trouvé'


class UserViewSet(AccessPolicyMixin, viewsets.ModelViewSet):
    swagger_tags = ['V1 - User']
    """
    ViewSet pour les opérations CRUD sur les utilisateurs.

    Fournit les actions standard : list, create, retrieve, update, destroy
    Plus des actions personnalisées pour la gestion des rôles et permissions.
    Les règles de hiérarchie (pas de montée en puissance, pas d'action sur soi-même, dernier superutilisateur)
    sont appliquées par AccessPolicy et chaque modification est inscrite au journal d'audit.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_value_regex = '[0-9]+'  # un identifiant non numérique est une route inconnue (404), pas une erreur serveur

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_service = UserService()

    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewUsers]
        elif self.action == 'create':
            permission_classes = [CanCreateUsers]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdateUsers]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteUsers]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Retourne la classe de sérialiseur appropriée selon l'action.
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    @staticmethod
    def _not_found():
        return Response({'error': NOT_FOUND_MESSAGE}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Lister tous les utilisateurs",
        responses={200: UserSerializer(many=True)},

        tags=['V1 - User']
    )
    def list(self, request):
        """
        Retourne la liste de tous les utilisateurs.
        """
        users = self.user_service.get_all_users()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Créer un nouvel utilisateur",
        request_body=UserCreateSerializer,
        responses={
            201: UserSerializer,
            400: "Données invalides",
            403: "Rôle plus puissant que le vôtre"
        },

        tags=['V1 - User']
    )
    def create(self, request):
        """
        Crée un nouvel utilisateur (les rôles attribués ne peuvent pas dépasser ceux de l'utilisateur connecté).
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                validated_data = serializer.validated_data.copy()
                validated_data.pop('password_confirm', None)  # Retirer la confirmation de mot de passe
                role_names = list(validated_data.get('role_names', []))

                self.policy.ensure_can_create_user(role_names)
                user = self.user_service.create_user(validated_data)
            except ValidationError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            audit_service.record(Actions.USER_CREATED, actor=request.user, target=user, target_label=user.email,
                                 request=request, metadata={'roles': role_names})
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Récupérer un utilisateur par son ID",
        responses={
            200: UserSerializer,
            404: "Utilisateur non trouvé"
        },

        tags=['V1 - User']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne un utilisateur spécifique par son ID.
        """
        user = self.user_service.get_user_by_id(pk)
        if user is None:
            return self._not_found()
        return Response(self.get_serializer(user).data)

    def _apply_update(self, request, pk, partial):
        user = self.user_service.get_user_by_id(pk)
        if user is None:
            return self._not_found()
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = dict(serializer.validated_data)
        try:
            self.policy.ensure_can_update_user(user, data)
            updated_user = self.user_service.update_user(user.pk, dict(data))
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        metadata = {'fields': sorted(name for name in data if name != 'role_names')}
        if 'role_names' in data:
            metadata['roles'] = list(data['role_names'])
        audit_service.record(Actions.USER_UPDATED, actor=request.user, target=updated_user,
                             target_label=updated_user.email, request=request, metadata=metadata)
        return Response(UserSerializer(updated_user).data)

    @swagger_auto_schema(
        operation_description="Mettre à jour un utilisateur",
        request_body=UserUpdateSerializer,
        responses={
            200: UserSerializer,
            400: "Données invalides",
            403: "Action refusée par la politique d'accès",
            404: "Utilisateur non trouvé"
        },

        tags=['V1 - User']
    )
    def update(self, request, pk=None):
        """
        Met à jour un utilisateur existant.
        """
        return self._apply_update(request, pk, partial=False)

    @swagger_auto_schema(
        operation_description="Mettre à jour partiellement un utilisateur",
        request_body=UserUpdateSerializer,
        responses={
            200: UserSerializer,
            400: "Données invalides",
            403: "Action refusée par la politique d'accès",
            404: "Utilisateur non trouvé"
        },

        tags=['V1 - User']
    )
    def partial_update(self, request, pk=None):
        """
        Met à jour partiellement un utilisateur existant.
        """
        return self._apply_update(request, pk, partial=True)

    @swagger_auto_schema(
        operation_description="Supprimer un utilisateur",
        responses={
            204: "Utilisateur supprimé avec succès",
            403: "Action refusée par la politique d'accès",
            404: "Utilisateur non trouvé"
        },

        tags=['V1 - User']
    )
    def destroy(self, request, pk=None):
        """
        Supprime un utilisateur existant (jamais soi-même, ni le dernier superutilisateur actif).
        """
        user = self.user_service.get_user_by_id(pk)
        if user is None:
            return self._not_found()
        self.policy.ensure_can_delete_user(user)

        user_id, email = user.pk, user.email
        self.user_service.delete_user(user_id)
        audit_service.record(Actions.USER_DELETED, actor=request.user, target_type='user', target_id=user_id,
                             target_label=email, request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        method='post',
        operation_description="Assigner des rôles à un utilisateur",
        request_body=UserRoleSerializer,
        responses={
            200: UserSerializer,
            400: "Données invalides",
            403: "Action refusée par la politique d'accès",
            404: "Utilisateur non trouvé"
        },

        tags=['V1 - User']
    )
    @action(detail=True, methods=['post'], permission_classes=[CanUpdateUsers])
    def assign_role(self, request, pk=None):
        """
        Assigne des rôles à un utilisateur (jamais un rôle plus puissant que le sien).
        """
        user = self.user_service.get_user_by_id(pk)
        if user is None:
            return self._not_found()
        serializer = UserRoleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        role_names = serializer.validated_data['role_names']
        try:
            for role_name in role_names:
                self.policy.ensure_can_assign_role(user, role_name)
            for role_name in role_names:
                self.user_service.assign_role_to_user(user.pk, role_name)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        audit_service.record(Actions.USER_ROLE_ASSIGNED, actor=request.user, target=user, target_label=user.email,
                             request=request, metadata={'roles': list(role_names)})
        return Response(UserSerializer(self.user_service.get_user_by_id(user.pk)).data)

    @swagger_auto_schema(
        method='post',
        operation_description="Retirer des rôles d'un utilisateur",
        request_body=UserRoleSerializer,
        responses={
            200: UserSerializer,
            400: "Données invalides",
            403: "Action refusée par la politique d'accès",
            404: "Utilisateur non trouvé"
        },

        tags=['V1 - User']
    )
    @action(detail=True, methods=['post'], permission_classes=[CanUpdateUsers])
    def remove_role(self, request, pk=None):
        """
        Retire des rôles d'un utilisateur.
        """
        user = self.user_service.get_user_by_id(pk)
        if user is None:
            return self._not_found()
        serializer = UserRoleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        role_names = serializer.validated_data['role_names']
        self.policy.ensure_can_remove_role(user)
        try:
            for role_name in role_names:
                self.user_service.remove_role_from_user(user.pk, role_name)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        audit_service.record(Actions.USER_ROLE_REMOVED, actor=request.user, target=user, target_label=user.email,
                             request=request, metadata={'roles': list(role_names)})
        return Response(UserSerializer(self.user_service.get_user_by_id(user.pk)).data)

    @swagger_auto_schema(
        method='get',
        operation_description="Obtenir les permissions d'un utilisateur",
        responses={
            200: openapi.Response(
                description="Liste des permissions",
                examples={
                    "application/json": {
                        "permissions": ["users.view", "users.create", "roles.view"]
                    }
                }
            ),
            404: "Utilisateur non trouvé"
        },

        tags=['V1 - User']
    )
    @action(detail=True, methods=['get'], permission_classes=[CanViewUsers])
    def permissions(self, request, pk=None):
        """
        Retourne toutes les permissions d'un utilisateur.
        """
        user = self.user_service.get_user_by_id(pk)
        if user is None:
            return self._not_found()
        return Response({'permissions': list(user.get_all_permissions())})

    @swagger_auto_schema(
        method='get',
        operation_description="Obtenir les rôles d'un utilisateur",
        responses={
            200: openapi.Response(
                description="Liste des rôles",
                examples={
                    "application/json": {
                        "roles": ["admin", "editor"]
                    }
                }
            ),
            404: "Utilisateur non trouvé"
        },

        tags=['V1 - User']
    )
    @action(detail=True, methods=['get'], permission_classes=[CanViewUsers])
    def roles(self, request, pk=None):
        """
        Retourne tous les rôles d'un utilisateur.
        """
        user = self.user_service.get_user_by_id(pk)
        if user is None:
            return self._not_found()
        return Response({'roles': user.get_roles()})

    @swagger_auto_schema(
        method='post',
        operation_description="Vérifier si un utilisateur a une permission spécifique",
        request_body=UserPermissionCheckSerializer,
        responses={
            200: openapi.Response(
                description="Résultat de la vérification",
                examples={
                    "application/json": {
                        "permission_code": "users.view",
                        "has_permission": True
                    }
                }
            ),
            400: "Code de permission requis",
            404: "Utilisateur non trouvé"
        },

        tags=['V1 - User']
    )
    @action(detail=True, methods=['post'], permission_classes=[CanViewUsers])
    def check_permission(self, request, pk=None):
        """
        Vérifie si un utilisateur a une permission spécifique.
        """
        user = self.user_service.get_user_by_id(pk)
        if user is None:
            return self._not_found()
        serializer = UserPermissionCheckSerializer(data=request.data)
        if serializer.is_valid():
            permission_code = serializer.validated_data['permission_code']
            return Response({
                'permission_code': permission_code,
                'has_permission': user.has_permission(permission_code)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='get',
        operation_description="Rechercher des utilisateurs par nom ou email",
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description="Terme de recherche (nom ou email)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: UserSerializer(many=True),
            400: "Terme de recherche requis"
        },

        tags=['V1 - User']
    )
    @action(detail=False, methods=['get'], permission_classes=[CanViewUsers])
    def search(self, request):
        """
        Recherche des utilisateurs par nom ou email.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'error': 'Terme de recherche requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        users = self.user_service.search_users(query)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
