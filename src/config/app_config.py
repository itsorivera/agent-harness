from pydantic import Field
from pydantic_settings import BaseSettings
from typing import ClassVar, List, Optional


class AppConfig(BaseSettings):
    """Application configuration"""

    # APP
    APP_TITLE: str = "Agent Harness API"
    API_VERSION: str = "1.0.0"
    API_AR_ROUTE: str = "/api/agent-harness"
    DEBUG: bool = False
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # LLMs Providers
    VALID_LLM_PROVIDERS: ClassVar[List[str]] = ["aws_bedrock", "ia_foundry"]
    DEFAULT_LLM_PROVIDER: str = "aws_bedrock"
    DEFAULT_LLM_MODEL: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    # API Keys
    HUGGINGFACE_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # Databases (Postgres)
    POSTGRES_CONNECTION_STRING: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[str] = None
    POSTGRES_DATABASE: Optional[str] = None
    CONVERSATION_SCHEMA: Optional[str] = "public"

    # Redis
    REDIS_HOST: Optional[str] = "localhost"
    REDIS_PORT: int = 6379

    # AWS Credentials
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"

    OLLAMA_SERVICE_URL: Optional[str] = None

    # Azure OpenAI / IAFoundry Configuration
    AZ_ENDPOINT: Optional[str] = None
    AZ_DEPLOY: Optional[str] = None
    AZ_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


config = AppConfig()