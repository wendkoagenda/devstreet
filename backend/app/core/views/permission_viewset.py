"""
ViewSet pour la gestion des permissions.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.core.models import Permission
from app.core.serializers import PermissionSerializer
from app.core.services.permission_service import PermissionService
from app.core.permissions.user_permission import CanViewPermissions
from collections import defaultdict



class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    swagger_tags = ['V1 - Permission']
    """
    ViewSet pour les opérations de lecture sur les permissions.
    
    Fournit les actions de lecture : list, retrieve
    Plus des actions personnalisées pour la consultation des permissions.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permission_service = PermissionService()

    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanViewPermissions]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister toutes les permissions",
        responses={200: PermissionSerializer(many=True)},
        security=[{'Bearer': []}],
        tags=['V1 - Permission']
    )
    def list(self, request):
        """
        Retourne la liste de toutes les permissions.
        """
        permissions = self.permission_service.get_all_permissions()
        serializer = self.get_serializer(permissions, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Récupérer une permission par son ID",
        responses={
            200: PermissionSerializer,
            404: "Permission non trouvée"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Permission']
    )
    def retrieve(self, request, pk=None):
        """
        Retourne les détails d'une permission spécifique.
        """
        try:
            permission = self.permission_service.get_permission_by_id(pk)
            serializer = self.get_serializer(permission)
            return Response(serializer.data)
        except Permission.DoesNotExist:
            return Response(
                {'error': 'Permission non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        method='get',
        operation_description="Rechercher des permissions par code ou nom",
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description="Terme de recherche (code ou nom)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: PermissionSerializer(many=True),
            400: "Terme de recherche requis"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Permission']
    )
    @action(detail=False, methods=['get'], permission_classes=[CanViewPermissions])
    def search(self, request):
        """
        Recherche des permissions par code ou nom.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'error': 'Terme de recherche requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permissions = self.permission_service.search_permissions(query)
        serializer = self.get_serializer(permissions, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_description="Obtenir les permissions d'un rôle spécifique",
        manual_parameters=[
            openapi.Parameter(
                'role_id',
                openapi.IN_QUERY,
                description="ID du rôle",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: PermissionSerializer(many=True),
            400: "ID du rôle requis"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Permission']
    )
    @action(detail=False, methods=['get'], permission_classes=[CanViewPermissions])
    def by_role(self, request):
        """
        Retourne toutes les permissions d'un rôle spécifique.
        """
        role_id = request.query_params.get('role_id')
        if not role_id:
            return Response(
                {'error': 'ID du rôle requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            permissions = self.permission_service.get_permissions_by_role(role_id)
            serializer = self.get_serializer(permissions, many=True)
            return Response(serializer.data)
        except (ValueError, ValidationError):
            # Identifiant mal formé : message générique, jamais le texte de l'exception interne
            return Response(
                {'error': 'Identifiant invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        method='get',
        operation_description="Obtenir les permissions d'un utilisateur spécifique",
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="ID de l'utilisateur",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: PermissionSerializer(many=True),
            400: "ID de l'utilisateur requis"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Permission']
    )
    @action(detail=False, methods=['get'], permission_classes=[CanViewPermissions])
    def by_user(self, request):
        """
        Retourne toutes les permissions d'un utilisateur spécifique.
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'ID de l\'utilisateur requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            permissions = self.permission_service.get_permissions_by_user(user_id)
            serializer = self.get_serializer(permissions, many=True)
            return Response(serializer.data)
        except (ValueError, ValidationError):
            # Identifiant mal formé : message générique, jamais le texte de l'exception interne
            return Response(
                {'error': 'Identifiant invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        method='get',
        operation_description="Obtenir le nombre de rôles utilisant cette permission",
        responses={
            200: openapi.Response(
                description="Nombre de rôles",
                examples={
                    "application/json": {
                        "permission_id": 1,
                        "role_count": 5
                    }
                }
            ),
            404: "Permission non trouvée"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Permission']
    )
    @action(detail=True, methods=['get'], permission_classes=[CanViewPermissions])
    def role_count(self, request, pk=None):
        """
        Retourne le nombre de rôles qui utilisent cette permission.
        """
        try:
            permission = self.permission_service.get_permission_by_id(pk)
            role_count = self.permission_service.get_role_count_for_permission(pk)
            return Response({
                'permission_id': pk,
                'role_count': role_count
            })
        except Permission.DoesNotExist:
            return Response(
                {'error': 'Permission non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        method='get',
        operation_description="Obtenir les statistiques d'utilisation d'une permission",
        responses={
            200: openapi.Response(
                description="Statistiques d'utilisation",
                examples={
                    "application/json": {
                        "permission_id": 1,
                        "role_count": 5,
                        "user_count": 25,
                        "created_at": "2023-01-01T00:00:00Z"
                    }
                }
            ),
            404: "Permission non trouvée"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Permission']
    )
    @action(detail=True, methods=['get'], permission_classes=[CanViewPermissions])
    def usage_stats(self, request, pk=None):
        """
        Retourne les statistiques d'utilisation d'une permission.
        """
        try:
            permission = self.permission_service.get_permission_by_id(pk)
            stats = self.permission_service.get_permission_usage_stats(pk)
            return Response(stats)
        except Permission.DoesNotExist:
            return Response(
                {'error': 'Permission non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        method='post',
        operation_description="Valider des codes de permission",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'codes': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description='Liste des codes de permission à valider'
                )
            },
            required=['codes']
        ),
        responses={
            200: openapi.Response(
                description="Résultats de validation",
                examples={
                    "application/json": {
                        "valid_codes": ["users.view", "roles.create"],
                        "invalid_codes": ["invalid.permission"]
                    }
                }
            ),
            400: "Codes requis"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Permission']
    )
    @action(detail=False, methods=['post'], permission_classes=[CanViewPermissions])
    def validate_codes(self, request):
        """
        Valide une liste de codes de permission.
        """
        codes = request.data.get('codes', [])
        if not codes:
            return Response(
                {'error': 'Codes requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validation_result = self.permission_service.validate_permission_codes(codes)
        return Response(validation_result)

    @swagger_auto_schema(
        method='get',
        operation_description="Obtenir des permissions par codes",
        manual_parameters=[
            openapi.Parameter(
                'codes',
                openapi.IN_QUERY,
                description="Codes de permission séparés par des virgules",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: PermissionSerializer(many=True),
            400: "Codes requis"
        },
        security=[{'Bearer': []}],
        tags=['V1 - Permission']
    )
    @action(detail=False, methods=['get'], permission_classes=[CanViewPermissions])
    def by_codes(self, request):
        """
        Retourne les permissions correspondant aux codes fournis.
        """
        codes_param = request.query_params.get('codes', '')
        if not codes_param:
            return Response(
                {'error': 'Codes requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        codes = [code.strip() for code in codes_param.split(',')]
        permissions = self.permission_service.get_permissions_by_codes(codes)
        serializer = self.get_serializer(permissions, many=True)
        return Response(serializer.data)



