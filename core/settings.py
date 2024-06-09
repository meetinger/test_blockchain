import logging
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

from project_root import PROJECT_ROOT


class Settings(BaseSettings):
    """Класс настроек"""

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / '.env', extra='allow')

    HTTP_PORT: int
    ROOT_PATH: str | None = None

    DB_NEO4J_HOST: str
    DB_NEO4J_PORT_BOLT: int
    DB_NEO4J_USER: str
    DB_NEO4J_PASS: str
    DB_NEO4J_NAME: str

    LOG_LEVEL: int = logging.INFO

    BLOCKCHAIR_TOKEN: str | None = None

    BLOCKCHAIR_DOWNLOADS_DIR: str = str((PROJECT_ROOT / "downloads").absolute())

    @property
    def neo4j_url(self):
        return f"bolt://{self.DB_NEO4J_USER}:{self.DB_NEO4J_PASS}@{self.DB_NEO4J_HOST}:{self.DB_NEO4J_PORT_BOLT}/{self.DB_NEO4J_NAME}"


settings = Settings()  # синглтон настроек
