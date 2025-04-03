import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Game Settings
    HINT_COST = 50
    BASE_POINTS = 100
    MAX_SPEED_BONUS = 100
    TIME_LIMIT = 300  # seconds
    BONUS_CHALLENGE_CHANCE = 0.3
    
    # Security
    ADMIN_KEY = os.getenv("ADMIN_KEY")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
    
    # Performance
    LLM_TIMEOUT = 3.0
    LLM_RETRIES = 3
    DYNAMIC_CONTENT_CACHE_SIZE = 100

settings = Settings()