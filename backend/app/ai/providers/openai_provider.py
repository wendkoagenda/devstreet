from app.ai.providers.openai_compatible import OpenAICompatibleProvider


def build_openai_provider() -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        name="openai",
        api_key_env="OPENAI_API_KEY",
        model_env="OPENAI_MODEL",
        default_model="gpt-4o-mini",
    )
