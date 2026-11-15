from unittest.mock import MagicMock

from django.test import SimpleTestCase, override_settings
from openai import APITimeoutError, RateLimitError

from app.ai.errors import ExternalUnavailable
from app.ai.providers.base import CompletionResult, LlmProvider
from app.ai.providers.openai_compatible import should_failover
from app.ai.providers.router import LlmRouter


class FakeProvider(LlmProvider):
    def __init__(self, name, *, configured=True, result=None, error=None):
        self.name = name
        self._configured = configured
        self._result = result
        self._error = error
        self.calls = 0

    def is_configured(self) -> bool:
        return self._configured

    def complete(self, messages, *, timeout=25.0):
        self.calls += 1
        if self._error:
            raise self._error
        return self._result


class LlmRouterTests(SimpleTestCase):
    def test_should_failover_on_timeout_and_rate_limit(self):
        self.assertTrue(should_failover(APITimeoutError(request=MagicMock())))
        self.assertTrue(should_failover(RateLimitError(
            message="rate", response=MagicMock(status_code=429), body=None
        )))
        self.assertTrue(should_failover(ExternalUnavailable("down")))

    @override_settings(AI_PRIMARY_PROVIDER="grok")
    def test_uses_grok_when_available(self):
        grok = FakeProvider(
            "grok",
            result=CompletionResult(content="ok", provider="grok", model="g"),
        )
        openai = FakeProvider(
            "openai",
            result=CompletionResult(content="alt", provider="openai", model="o"),
        )
        result = LlmRouter(primary=grok, fallback=openai).complete(
            [{"role": "user", "content": "hi"}]
        )
        self.assertEqual(result.provider, "grok")
        self.assertEqual(grok.calls, 1)
        self.assertEqual(openai.calls, 0)

    @override_settings(AI_PRIMARY_PROVIDER="grok")
    def test_fails_over_to_openai_on_grok_timeout(self):
        grok = FakeProvider("grok", error=APITimeoutError(request=MagicMock()))
        openai = FakeProvider(
            "openai",
            result=CompletionResult(content="fallback", provider="openai", model="o"),
        )
        result = LlmRouter(primary=grok, fallback=openai).complete(
            [{"role": "user", "content": "hi"}]
        )
        self.assertEqual(result.provider, "openai")
        self.assertEqual(result.content, "fallback")
        self.assertEqual(result.failover_reason, "timeout")
        self.assertEqual(grok.calls, 1)
        self.assertEqual(openai.calls, 1)

    def test_503_when_no_provider_configured(self):
        grok = FakeProvider("grok", configured=False)
        openai = FakeProvider("openai", configured=False)
        with self.assertRaises(ExternalUnavailable):
            LlmRouter(primary=grok, fallback=openai).complete(
                [{"role": "user", "content": "hi"}]
            )


class StripReasoningTests(SimpleTestCase):
    """Le raisonnement d'un modèle (<think>…</think>) ne doit pas polluer la réponse."""

    def test_retire_le_bloc_de_raisonnement(self):
        from app.ai.providers.openai_compatible import strip_reasoning

        raw = '<think>Je dois produire {"title": 1} puis...</think>\n{"title": "Dev"}'
        self.assertEqual(strip_reasoning(raw), '{"title": "Dev"}')

    def test_reponse_sans_raisonnement_inchangee(self):
        from app.ai.providers.openai_compatible import strip_reasoning

        self.assertEqual(strip_reasoning('  {"a": 1}  '), '{"a": 1}')
        self.assertEqual(strip_reasoning(""), "")
