"""Client chat.completions compatible OpenAI / xAI Grok."""

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    OpenAIError,
    RateLimitError,
)

from app.ai.conf import config
from app.ai.errors import ExternalUnavailable
from app.ai.providers.base import CompletionResult, LlmProvider


class OpenAICompatibleProvider(LlmProvider):
    def __init__(
        self,
        *,
        name: str,
        api_key_env: str,
        model_env: str,
        default_model: str,
        base_url_env: str | None = None,
        default_base_url: str | None = None,
    ):
        self.name = name
        self._api_key_env = api_key_env
        self._model_env = model_env
        self._default_model = default_model
        self._base_url_env = base_url_env
        self._default_base_url = default_base_url

    def is_configured(self) -> bool:
        return bool(config(self._api_key_env).strip())

    def _model(self) -> str:
        return (config(self._model_env) or self._default_model).strip()

    def _base_url(self) -> str | None:
        if not self._base_url_env:
            return self._default_base_url
        return (config(self._base_url_env) or self._default_base_url or "").strip() or None

    def complete(self, messages: list[dict], *, timeout: float = 25.0) -> CompletionResult:
        api_key = config(self._api_key_env).strip()
        if not api_key:
            raise ExternalUnavailable(f"Clé {self.name} absente côté serveur.")
        model = self._model()
        if not model:
            raise ExternalUnavailable(f"Modèle {self.name} non configuré.")
        try:
            with OpenAI(
                api_key=api_key,
                base_url=self._base_url(),
                timeout=timeout,
                max_retries=0,
            ) as client:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=2000,
                    temperature=0.3,
                )
        except OpenAIError as error:
            detail = getattr(error, "message", None) or str(error)
            detail = detail.strip()[:300] or f"{self.name} indisponible"
            raise ExternalUnavailable(
                f"Fournisseur {self.name} indisponible : {detail}"
            ) from error

        choice = response.choices[0] if response.choices else None
        content = (choice.message.content or "").strip() if choice else ""
        if not content:
            raise ExternalUnavailable(f"Réponse vide de {self.name}.")
        usage = response.usage
        return CompletionResult(
            content=content,
            provider=self.name,
            model=model,
            input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            output_tokens=getattr(usage, "completion_tokens", 0) or 0,
        )


def should_failover(error: Exception) -> bool:
    """Indique si l'erreur justifie une bascule vers le fournisseur de secours."""
    if isinstance(error, (APITimeoutError, APIConnectionError, RateLimitError)):
        return True
    if isinstance(error, APIStatusError):
        status = getattr(error, "status_code", None) or 0
        if status in (402, 404, 408, 429) or status >= 500:
            return True
        # Certains comptes renvoient 401/403 quand le quota est épuisé.
        if status in (401, 403):
            message = str(error).lower()
            markers = ("quota", "rate", "billing", "limit", "exhausted", "credit")
            return any(marker in message for marker in markers)
    if isinstance(error, ExternalUnavailable):
        return True
    return False


def failover_reason(error: Exception) -> str:
    if isinstance(error, APITimeoutError):
        return "timeout"
    if isinstance(error, APIConnectionError):
        return "connection"
    if isinstance(error, RateLimitError):
        return "rate_limit"
    if isinstance(error, APIStatusError):
        return f"http_{getattr(error, 'status_code', 'error')}"
    if isinstance(error, ExternalUnavailable):
        return "unavailable"
    return "provider_error"
