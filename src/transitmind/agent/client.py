from openai import OpenAI
from transitmind.config import settings
from transitmind.logging_config import configure_logging

# Number of responses from the LLM to look at
NUM_RESPONSES = 0

# Set Logging
configure_logging(log_level=settings.log_level)

# Create LLM Client
client = OpenAI(api_key=settings.openai_api_key)