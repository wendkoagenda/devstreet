"""Vues des invitations d'entreprise : gestion par le propriétaire, consultation et acceptation par l'invité."""
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.marketplace.services.invitation_service import InvitationService


class InvitationCreateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True, default="")


@swagger_auto_schema(method="post", request_body=InvitationCreateSerializer, tags=["V1 - Invitations d'entreprise"])
@swagger_auto_schema(method="get", tags=["V1 - Invitations d'entreprise"])
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def my_invitations(request):
    """GET /marketplace/me/invitations : invitations de mon entreprise. POST : en crée une (propriétaire)."""
    if request.method == "POST":
        serializer = InvitationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = InvitationService.create(request.user, serializer.validated_data["email"])
        return Response(data, status=status.HTTP_201_CREATED)
    return Response(InvitationService.list_for_owner(request.user))


@swagger_auto_schema(method="delete", tags=["V1 - Invitations d'entreprise"])
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def my_invitation(request, invitation_id):
    """DELETE /marketplace/me/invitations/<id> : révoque une invitation en attente (propriétaire)."""
    return Response(InvitationService.revoke(request.user, invitation_id))


@swagger_auto_schema(method="get", tags=["V1 - Invitations d'entreprise"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def invitation_detail(request, token):
    """GET /marketplace/invitations/<jeton> : entreprise et état de l'invitation (valide, expirée, révoquée, utilisée)."""
    return Response(InvitationService.detail(request.user, token))


@swagger_auto_schema(method="post", tags=["V1 - Invitations d'entreprise"])
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def invitation_accept(request, token):
    """POST /marketplace/invitations/<jeton>/accept : rejoint l'entreprise (profil entreprise non propriétaire)."""
    return Response(InvitationService.accept(request.user, token), status=status.HTTP_201_CREATED)
