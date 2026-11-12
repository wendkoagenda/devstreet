from dataclasses import dataclass


@dataclass(frozen=True)
class CompletionResult:
    content: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    failover_reason: str = ""


class LlmProvider:
    """Contrat minimal d'un fournisseur de complétion chat."""

    name: str = "base"

    def is_configured(self) -> bool:
        raise NotImplementedError

    def complete(self, messages: list[dict], *, timeout: float = 25.0) -> CompletionResult:
        raise NotImplementedError
