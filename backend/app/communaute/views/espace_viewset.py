"""
ViewSet pour la gestion des espaces (communautés).
"""
from django.core.exceptions import ValidationError
from django.db.models import Count
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.communaute.models import Espace
from app.communaute.serializers import (
    EspaceSerializer,
    LienInvitationSerializer,
    MessageGroupeSerializer,
    ParticipationEspaceSerializer,
)
from app.communaute.services.espace_service import EspaceService


def _err(exc: ValidationError) -> str:
    if hasattr(exc, 'messages'):
        return '; '.join(str(m) for m in exc.messages)
    if hasattr(exc, 'message'):
        return str(exc.message)
    return str(exc)


class EspaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations sur les espaces / communautés.
    """

    swagger_tags = ['V1 - Espace']
    queryset = Espace.objects.all()
    serializer_class = EspaceSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.espace_service = EspaceService()

    def get_permissions(self):
        return [IsAuthenticated()]

    @swagger_auto_schema(tags=['V1 - Espace'])
    def list(self, request):
        mine_raw = (request.query_params.get('mine') or '').strip().lower()
        mine_only = mine_raw in ('1', 'true', 'yes', 'moi')
        try:
            espaces = self.espace_service.get_all(
                search=request.query_params.get('search'),
                ordering=request.query_params.get('ordering'),
                type_filter=request.query_params.get('type') or 'COMMUNAUTE',
                acces_filter=request.query_params.get('acces'),
                visible_for=request.user,
                mine_only=mine_only,
            ).annotate(membres_count=Count('participations'))
        except ValueError:
            return Response({'error': 'Tri invalide'}, status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(espaces)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(tags=['V1 - Espace'])
    def retrieve(self, request, pk=None):
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND,
            )
        invite = request.query_params.get('invite')
        access = self.espace_service.resolve_access(
            espace=espace, acteur=request.user, invite_code=invite
        )
        # Accès LIEN sans membership : méta visible seulement avec invite valide
        if espace.acces == EspaceService.ACCES_LIEN and access.participation is None:
            if not invite or self.espace_service.find_active_lien(invite) is None:
                return Response(
                    {'error': 'Espace non trouvé'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            lien = self.espace_service.find_active_lien(invite)
            if lien is None or lien.espace_id != espace.id:
                return Response(
                    {'error': 'Espace non trouvé'},
                    status=status.HTTP_404_NOT_FOUND,
                )
        serializer = self.get_serializer(espace)
        data = serializer.data
        data['can_read'] = access.can_read
        data['can_interact'] = access.can_interact
        data['can_publish'] = access.can_publish
        data['via_preview'] = access.via_preview
        return Response(data)

    @swagger_auto_schema(tags=['V1 - Espace'])
    def create(self, request):
        try:
            type_espace = (
                request.data.get('type') or EspaceService.TYPE_COMMUNAUTE
            )
            if str(type_espace).upper() == EspaceService.TYPE_CHAINE:
                espace = self.espace_service.create_chaine(
                    createur=request.user,
                    nom=request.data.get('nom', ''),
                    description=request.data.get('description', ''),
                    acces=request.data.get('acces', EspaceService.ACCES_PUBLIC),
                    commentaires_ouverts=request.data.get(
                        'commentaires_ouverts', True
                    ),
                )
            else:
                espace = self.espace_service.create_communaute(
                    createur=request.user,
                    nom=request.data.get('nom', ''),
                    description=request.data.get('description', ''),
                    membres_peuvent_publier=request.data.get(
                        'membres_peuvent_publier', True
                    ),
                    acces=request.data.get('acces', EspaceService.ACCES_PUBLIC),
                )
            serializer = self.get_serializer(espace)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['V1 - Espace'])
    def partial_update(self, request, pk=None):
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            if 'membres_peuvent_publier' in request.data:
                espace = self.espace_service.set_membres_peuvent_publier(
                    espace=espace,
                    acteur=request.user,
                    value=bool(request.data.get('membres_peuvent_publier')),
                )
            if 'acces' in request.data:
                espace = self.espace_service.set_acces(
                    espace=espace,
                    acteur=request.user,
                    acces=request.data.get('acces'),
                )
            if 'commentaires_ouverts' in request.data:
                espace = self.espace_service.set_commentaires_ouverts(
                    espace=espace,
                    acteur=request.user,
                    value=bool(request.data.get('commentaires_ouverts')),
                )
            if any(k in request.data for k in ('nom', 'description', 'photo')):
                espace = self.espace_service.update_infos(
                    espace=espace,
                    acteur=request.user,
                    nom=request.data.get('nom') if 'nom' in request.data else None,
                    description=(
                        request.data.get('description')
                        if 'description' in request.data
                        else None
                    ),
                    photo=request.data.get('photo') if 'photo' in request.data else None,
                )
            return Response(self.get_serializer(espace).data)
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['V1 - Espace'])
    def update(self, request, pk=None):
        return self.partial_update(request, pk=pk)

    @swagger_auto_schema(tags=['V1 - Espace'])
    def destroy(self, request, pk=None):
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            self.espace_service._assert_super_admin(
                espace=espace, acteur=request.user
            )
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_403_FORBIDDEN)
        self.espace_service.delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(tags=['V1 - Espace'])
    @action(detail=True, methods=['post'], url_path='rejoindre')
    def rejoindre(self, request, pk=None):
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            if espace.type == EspaceService.TYPE_CHAINE:
                participation = self.espace_service.s_abonner_chaine(
                    espace=espace,
                    membre=request.user,
                )
            else:
                participation = self.espace_service.rejoindre_communaute_publique(
                    espace=espace,
                    membre=request.user,
                )
            return Response(
                ParticipationEspaceSerializer(participation).data,
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['V1 - Espace'])
    @action(detail=True, methods=['post'], url_path='quitter')
    def quitter(self, request, pk=None):
        """Se désabonner / quitter (sauf SUPER_ADMIN)."""
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            self.espace_service.se_desabonner(
                espace=espace, membre=request.user
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(methods=['get', 'post'], tags=['V1 - Espace'])
    @action(detail=True, methods=['get', 'post'], url_path='liens')
    def liens(self, request, pk=None):
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            if request.method == 'GET':
                liens = self.espace_service.list_liens(
                    espace=espace, acteur=request.user
                )
                page = self.paginate_queryset(liens)
                serializer = LienInvitationSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            lien, code = self.espace_service.create_lien(
                espace=espace,
                acteur=request.user,
                previsualisation_autorisee=bool(
                    request.data.get('previsualisation_autorisee', False)
                ),
            )
            data = LienInvitationSerializer(lien).data
            data['code'] = code
            return Response(data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['V1 - Espace'])
    @action(
        detail=True,
        methods=['post'],
        url_path=r'liens/(?P<lien_id>[0-9]+)/revoquer',
    )
    def revoquer_lien(self, request, pk=None, lien_id=None):
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            lien = self.espace_service.revoquer_lien(
                espace=espace,
                acteur=request.user,
                lien_id=int(lien_id),
            )
            return Response(LienInvitationSerializer(lien).data)
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _serialize_message(self, message):
        return MessageGroupeSerializer(
            message, context={'request': self.request}
        ).data

    @swagger_auto_schema(methods=['get', 'post'], tags=['V1 - Espace'])
    @action(detail=True, methods=['get', 'post'], url_path='messages')
    def messages(self, request, pk=None):
        """Chat de communauté : liste ou envoi d'un message."""
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            if request.method == 'GET':
                qs = self.espace_service.list_messages_groupe(
                    espace=espace, acteur=request.user
                )
                from app.communaute.services.activity_service import (
                    ActivityService,
                )

                ActivityService().mark_espace_read(
                    espace_id=espace.id, acteur=request.user
                )
                page = self.paginate_queryset(qs)
                if page is not None:
                    return self.get_paginated_response(
                        MessageGroupeSerializer(
                            page, many=True, context={'request': request}
                        ).data
                    )
                return Response(
                    MessageGroupeSerializer(
                        qs, many=True, context={'request': request}
                    ).data
                )
            reply_raw = request.data.get('reply_to_id', None)
            reply_to_id = None
            if reply_raw not in (None, '', 'null'):
                try:
                    reply_to_id = int(reply_raw)
                except (TypeError, ValueError) as exc:
                    raise ValidationError(
                        'reply_to_id invalide.'
                    ) from exc
            message = self.espace_service.envoyer_message_groupe(
                espace=espace,
                auteur=request.user,
                texte=request.data.get('texte', ''),
                reply_to_id=reply_to_id,
            )
            message = (
                self.espace_service.list_messages_groupe(
                    espace=espace, acteur=request.user
                ).filter(id=message.id).first()
                or message
            )
            return Response(
                self._serialize_message(message),
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['V1 - Espace'])
    @action(
        detail=True,
        methods=['post'],
        url_path=r'messages/(?P<message_id>[0-9]+)/supprimer',
    )
    def supprimer_message(self, request, pk=None, message_id=None):
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            message = self.espace_service.supprimer_message_groupe(
                espace=espace,
                acteur=request.user,
                message_id=int(message_id),
            )
            return Response(self._serialize_message(message))
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['V1 - Espace'])
    @action(
        detail=True,
        methods=['post'],
        url_path=r'messages/(?P<message_id>[0-9]+)/reactions',
    )
    def reactions_message(self, request, pk=None, message_id=None):
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            message = self.espace_service.toggle_reaction_message_groupe(
                espace=espace,
                acteur=request.user,
                message_id=int(message_id),
                emoji=request.data.get('emoji', ''),
            )
            return Response(self._serialize_message(message))
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['V1 - Espace'])
    @action(detail=True, methods=['get'], url_path='membres')
    def membres(self, request, pk=None):
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            membres = self.espace_service.list_membres(
                espace=espace, acteur=request.user
            )
            page = self.paginate_queryset(membres)
            if page is not None:
                return self.get_paginated_response(
                    ParticipationEspaceSerializer(page, many=True).data
                )
            return Response(
                ParticipationEspaceSerializer(membres, many=True).data
            )
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['V1 - Espace'])
    @action(
        detail=True,
        methods=['post'],
        url_path=r'membres/(?P<membre_id>[0-9]+)/role',
    )
    def set_role(self, request, pk=None, membre_id=None):
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            participation = self.espace_service.set_membre_role(
                espace=espace,
                acteur=request.user,
                membre_id=int(membre_id),
                role=request.data.get('role', ''),
            )
            return Response(
                ParticipationEspaceSerializer(participation).data
            )
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['V1 - Espace'])
    @action(
        detail=True,
        methods=['post'],
        url_path=r'membres/(?P<membre_id>[0-9]+)/exclure',
    )
    def exclure_membre(self, request, pk=None, membre_id=None):
        espace = self.espace_service.get_by_id(pk)
        if not espace:
            return Response(
                {'error': 'Espace non trouvé'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            self.espace_service.exclure_membre(
                espace=espace,
                acteur=request.user,
                membre_id=int(membre_id),
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['V1 - Espace'])
    @action(
        detail=False,
        methods=['get'],
        url_path=r'invitation/(?P<code>[^/.]+)',
    )
    def invitation_preview(self, request, code=None):
        try:
            payload = self.espace_service.preview_invitation(
                code=code, acteur=request.user
            )
            return Response(payload)
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['V1 - Espace'])
    @action(
        detail=False,
        methods=['post'],
        url_path=r'invitation/(?P<code>[^/.]+)/rejoindre',
    )
    def invitation_rejoindre(self, request, code=None):
        try:
            participation = self.espace_service.rejoindre_via_lien(
                code=code, membre=request.user
            )
            return Response(
                ParticipationEspaceSerializer(participation).data,
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({'error': _err(e)}, status=status.HTTP_400_BAD_REQUEST)
