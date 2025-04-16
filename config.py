import os
from dotenv import load_dotenv

load_dotenv()

#API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

#Model Configuration
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

#Debate Configuration
DEFAULT_TOPIC = "Artificial General Intelligence poses an existential risk to humanity"
DEFAULT_ROUNDS = 2