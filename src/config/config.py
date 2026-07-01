from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    TomlConfigSettingsSource,
)

class CORS(BaseModel):
    origins: list[str] = []

class Database(BaseModel):
    postgres_username: str = ""
    postgres_db: str = ""
    postgres_port: int = 5432
    postgres_host: str = ""
    postgres_password: str = ""
    alembic_postgres_host: str | None = None

    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def alembic_url(self) -> str:
        host = self.alembic_postgres_host or self.postgres_host
        return f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{host}:{self.postgres_port}/{self.postgres_db}"

class S3(BaseModel):
    ENDPOINT_URL: str = "https://storage.yandexcloud.net"
    ACCESS_KEY_ID: str = "change-me-in-production"
    ACCESS_SECRET_KEY: str = "change-me-in-production"
    BUCKET_NAME: str = "query-point"
    REGION: str = "ru-central1"

class JWT(BaseModel):
    SECRET_KEY: str = ""
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 0
    REFRESH_TOKEN_EXPIRE_DAYS: int = 0

class ElasticSearch(BaseModel):
    URL: str = ""

class Config(BaseSettings):
    model_config = SettingsConfigDict(toml_file="config.toml")

    database: Database = Database()
    cors: CORS = CORS()
    s3: S3 = S3()
    jwt: JWT = JWT()
    elasticsearch: ElasticSearch = ElasticSearch()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


config = Config()
