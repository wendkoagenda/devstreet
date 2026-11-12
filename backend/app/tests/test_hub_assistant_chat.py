from unittest.mock import patch

from app.ai.providers.base import CompletionResult
from app.tests.devstreet_hub_base import DevStreetHubAPITestCase


class HubAssistantChatTests(DevStreetHubAPITestCase):
    @patch("app.ai.services.chat_service.LlmRouter.complete")
    def test_project_assistant_chat(self, complete):
        complete.return_value = CompletionResult(
            content="Critère : export CSV lisible.",
            provider="openai",
            model="gpt-4o-mini",
            failover_reason="timeout",
        )
        project = self.project()
        response = self.client.post(
            f"/api/v1/projects/{project.pk}/assistant/chat",
            {"message": "Propose un critère", "include_repo": False},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["provider"], "openai")
        self.assertEqual(response.data["failover_reason"], "timeout")
        self.assertIn("Critère", response.data["assistant_message"])
        complete.assert_called_once()
        messages = complete.call_args.args[0]
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn(project.title, messages[0]["content"])
