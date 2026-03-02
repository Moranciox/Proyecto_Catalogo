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

    # -------------------------
    # Catálogo
    # -------------------------
    # LP por defecto para precio en ventas.detalle_lp_vendedor
    DEFAULT_LP: int = 7
    # Umbral anti-basura (precios muy chicos suelen ser registros inválidos/de prueba)
    CATALOG_MIN_PRICE: float = 500
    # Sub-familias NO alcohólicas que igual deben aparecer (ej: energéticas)
    # Formato: "481,123" (se parsea donde se use)
    NON_ALCOHOL_SUBFAMILIAS: str = "481"

    class Config:
        env_file = ".env"

settings = Settings()
