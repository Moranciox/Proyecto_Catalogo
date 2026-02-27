from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # INTEGRA (interna)
    INTEGRA_PG_NAME: str
    INTEGRA_PG_USER: str
    INTEGRA_PG_PASSWORD: str
    INTEGRA_PG_HOST: str
    INTEGRA_PG_PORT: int = 5432

    # EXT (externa/local)
    EXT_PG_NAME: str
    EXT_PG_USER: str
    EXT_PG_PASSWORD: str
    EXT_PG_HOST: str
    EXT_PG_PORT: int = 5432

    # CORS
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"

settings = Settings()
