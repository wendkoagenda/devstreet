import logging

from openai import OpenAIError

from app.ai.conf import config
from app.ai.errors import ExternalUnavailable
from app.ai.providers.base import CompletionResult, LlmProvider
from app.ai.providers.grok import build_grok_provider
from app.ai.providers.openai_compatible import failover_reason, should_failover
from app.ai.providers.openai_provider import build_openai_provider

logger = logging.getLogger(__name__)


class LlmRouter:
    """Grok en primaire, OpenAI en secours automatique."""

    def __init__(
        self,
        primary: LlmProvider | None = None,
        fallback: LlmProvider | None = None,
    ):
        self.primary = primary or build_grok_provider()
        self.fallback = fallback or build_openai_provider()

    def _preferred_order(self) -> list[LlmProvider]:
        preferred = (config("PRIMARY_PROVIDER") or "grok").strip().lower()
        if preferred == "openai":
            return [self.fallback, self.primary]
        return [self.primary, self.fallback]

    def complete(self, messages: list[dict], *, timeout: float = 25.0) -> CompletionResult:
        providers = [p for p in self._preferred_order() if p.is_configured()]
        if not providers:
            raise ExternalUnavailable(
                "Aucun fournisseur IA configuré (AI_GROK_API_KEY ou AI_OPENAI_API_KEY)."
            )

        last_error: Exception | None = None
        for index, provider in enumerate(providers):
            try:
                result = provider.complete(messages, timeout=timeout)
                if index > 0 and last_error is not None:
                    return CompletionResult(
                        content=result.content,
                        provider=result.provider,
                        model=result.model,
                        input_tokens=result.input_tokens,
                        output_tokens=result.output_tokens,
                        failover_reason=failover_reason(last_error),
                    )
                return result
            except (OpenAIError, ExternalUnavailable) as error:
                last_error = error
                has_next = index + 1 < len(providers)
                if not has_next or not should_failover(error):
                    if isinstance(error, ExternalUnavailable):
                        raise
                    raise ExternalUnavailable(
                        f"Fournisseur {provider.name} indisponible."
                    ) from error
                logger.warning(
                    "IA failover %s -> suivant (%s)",
                    provider.name,
                    failover_reason(error),
                )

        raise ExternalUnavailable("Tous les fournisseurs IA ont échoué.")
