from unittest.mock import patch

from django.test import override_settings
from rest_framework.test import APITestCase

from app.ai.providers.base import CompletionResult
from app.core.models import Permission, Role
from django.contrib.auth import get_user_model


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class AiChatApiTests(APITestCase):
    def setUp(self):
        role = Role.objects.create(name="AI Tester")
        perm, _ = Permission.objects.get_or_create(
            code="ai.chat", defaults={"description": "chat"}
        )
        role.permissions.add(perm)
        User = get_user_model()
        self.user = User.objects.create_user(
            username="chatuser",
            email="chat@example.test",
            password="Strong-Password-42!",
        )
        self.user.roles.add(role)
        self.client.force_authenticate(self.user)

    @patch("app.ai.services.chat_service.LlmRouter.complete")
    def test_conversation_and_message_flow(self, complete):
        complete.return_value = CompletionResult(
            content="Voici une piste.",
            provider="grok",
            model="grok-3-mini",
        )
        create = self.client.post(
            "/api/v1/ai/conversations",
            {"consumer": "generic", "title": "Test"},
            format="json",
        )
        self.assertEqual(create.status_code, 201, create.data)
        conversation_id = create.data["id"]

        reply = self.client.post(
            f"/api/v1/ai/conversations/{conversation_id}/messages",
            {"content": "Comment démarrer ?", "context_text": "Projet démo"},
            format="json",
        )
        self.assertEqual(reply.status_code, 200, reply.data)
        self.assertEqual(reply.data["provider"], "grok")
        self.assertEqual(reply.data["assistant_message"], "Voici une piste.")
        self.assertEqual(reply.data["conversation_id"], conversation_id)

        detail = self.client.get(f"/api/v1/ai/conversations/{conversation_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(len(detail.data["messages"]), 2)

    def test_forbidden_without_permission(self):
        User = get_user_model()
        outsider = User.objects.create_user(
            username="noai",
            email="noai@example.test",
            password="Strong-Password-42!",
        )
        self.client.force_authenticate(outsider)
        response = self.client.post(
            "/api/v1/ai/conversations", {"consumer": "generic"}, format="json"
        )
        self.assertEqual(response.status_code, 403)
