try:
    from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    BaseSettings = object  # type: ignore
    SettingsConfigDict = dict  # type: ignore

class Settings(BaseSettings):
    # OpenAI API Settings
    OPENAI_API_KEY: str | None = None # Allow key to be optional to enable server startup
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MODEL_CHEAT_CHECK: str = "qwen3-235b-a22b"
    # JWT Settings
    SECRET_KEY: str = 'dev-secret-change-me'
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 600

    # Server Settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    UVICORN_RELOAD: bool = True

    # Point to the .env file in the 'backend' directory relative to the project root
    model_config = SettingsConfigDict(env_file="backend/.env")

# Create a single instance of the settings
settings = Settings()
