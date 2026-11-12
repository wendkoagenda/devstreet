import hashlib
import hmac
from rest_framework.permissions import BasePermission
from app.projects.conf import config
from app.projects.services.errors import ExternalUnavailable


class SignedGiteaWebhook(BasePermission):
    message = "Signature du webhook invalide."

    def has_permission(self, request, view):
        secret = config("GITEA_WEBHOOK_SECRET")
        if not secret:
            raise ExternalUnavailable("Webhook non configuré.")
        expected = hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(
            request.headers.get("X-Gitea-Signature", ""), expected
        )
