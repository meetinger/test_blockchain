import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

from project_root import PROJECT_ROOT


class Settings(BaseSettings):
    """Класс настроек"""

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / '.env')

    HTTP_PORT: int
    ROOT_PATH: str

    DB_NEO4J_HOST: str
    DB_NEO4J_PORT: int
    DB_NEO4J_USER: str
    DB_NEO4J_PASS: str
    DB_NEO4J_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USER: str
    REDIS_PASS: str

    TOKEN_UPDATE_TIME: int

    LOG_LEVEL: int = logging.INFO

    BLOCKCHAIR_TOKEN: str = None

    @property
    def neo4j_url(self):
        return f"bolt://{self.DB_NEO4J_HOST}:{self.DB_NEO4J_PORT}/{self.DB_NEO4J_NAME}"

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PSW}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()  # синглтон настроек
