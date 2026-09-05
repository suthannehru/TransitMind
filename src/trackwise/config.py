from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Config
    anthropic_api_key: str
    openai_api_key: str
    llm_provider: str
    llm_model: str

    # Services Config
    qdrant_url: str
    redis_url: str

    # MTA Data
    mta_feed_base_url: str

    # App Config
    log_level: str
    agent_max_iterations: int

    model_config = SettingsConfigDict(env_file=".env")