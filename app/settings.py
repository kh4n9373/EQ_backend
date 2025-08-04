import os

from dotenv import load_dotenv

load_dotenv()

# Database settings
DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/eq_test_db"
)

# JWT settings
SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Google OAuth settings
GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

# OpenAI settings
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# CORS settings
CORS_ORIGINS: list = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# Add any additional CORS origins from environment
if os.getenv("CORS_ORIGINS"):
    CORS_ORIGINS.extend(os.getenv("CORS_ORIGINS", "").split(","))

# Environment
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
DEBUG: bool = ENVIRONMENT == "development"
