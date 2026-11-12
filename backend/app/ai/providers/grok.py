from app.ai.providers.openai_compatible import OpenAICompatibleProvider


def build_grok_provider() -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        name="grok",
        api_key_env="GROK_API_KEY",
        model_env="GROK_MODEL",
        default_model="qwen/qwen3.8-27b",
        base_url_env="GROK_BASE_URL",
        default_base_url="https://api.groq.com/openai/v1",
    )
