from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Config
    anthropic_api_key: str
    openai_api_key: str
    llm_provider: str
    llm_model: str
    input_price_per_million: float
    output_price_per_million: float
    llm_judge_model: str
    llm_judge_input_price_per_million: float
    llm_judge_output_price_per_million: float

    # Services Config
    qdrant_url: str
    redis_url: str

    # MTA Data
    mta_feed_base_url: str

    # App Config
    log_level: str
    agent_max_iterations: int

    # Use LangGraph Implementation
    use_graph: bool = True

    model_config = SettingsConfigDict(env_file=".env")

# Instantiate settings
settings = Settings()