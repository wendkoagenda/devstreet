"""Tests mentions forum @selina."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from app.ai.selina_user import ensure_selina_user
from app.communaute.models import Commentaire, Publication
from app.communaute.services.commentaire_service import CommentaireService
from app.core.models import Permission, Role


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class SelinaMentionTests(TestCase):
    def setUp(self):
        role = Role.objects.create(name="Selina Mention Tester")
        perm, _ = Permission.objects.get_or_create(
            code="ai.chat", defaults={"description": "chat"}
        )
        role.permissions.add(perm)
        User = get_user_model()
        self.user = User.objects.create_user(
            username="mentioner",
            email="mentioner@example.test",
            password="Strong-Password-42!",
        )
        self.user.roles.add(role)
        self.selina = ensure_selina_user()
        self.publication = Publication.objects.create(
            auteur=self.user,
            type="DISCUSSION",
            titre="Test Selina",
            description="Besoin d'aide sur React.",
            created_by=self.user.id,
            updated_by=self.user.id,
        )
        self.service = CommentaireService()

    @patch("app.ai.services.chat_service.ChatService.chat")
    def test_mention_creates_selina_reply(self, chat):
        chat.return_value = {
            "conversation_id": 1,
            "user_message": "@selina comment faire ?",
            "assistant_message": "Voici une piste pour React.",
            "provider": "grok",
            "model": "grok-3-mini",
            "failover_reason": None,
            "message_id": 2,
        }

        comment = self.service.create_commentaire(
            publication_id=self.publication.id,
            auteur=self.user,
            texte="@selina comment faire ?",
            created_by=self.user.id,
            updated_by=self.user.id,
        )
        self.assertIsNotNone(comment)
        chat.assert_called_once()

        replies = Commentaire.objects.filter(
            parent_id=comment.id, auteur=self.selina
        )
        self.assertEqual(replies.count(), 1)
        self.assertIn("React", replies.first().texte)

    @patch("app.ai.services.chat_service.ChatService.chat")
    def test_no_mention_skips_selina(self, chat):
        self.service.create_commentaire(
            publication_id=self.publication.id,
            auteur=self.user,
            texte="Salut tout le monde",
            created_by=self.user.id,
            updated_by=self.user.id,
        )
        chat.assert_not_called()
        self.assertEqual(
            Commentaire.objects.filter(auteur=self.selina).count(), 0
        )
