"""Environment-backed settings for the backend, loaded from backend/.env.

Static values that are not environment-specific belong in consts.py.

    from settings import settings
    client = MongoClient(settings.mongodb_url)
"""

from pathlib import Path
from urllib.parse import quote_plus

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    # env_file is an absolute path so the process can be started from any directory.
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mongodb_username: str
    mongodb_password: SecretStr
    mongodb_host: str = None
    mongodb_name: str = None
    counter_window_length: int = 10
    domain_name: str = None
    secret_key: str = None
    algorithm: str = None


    @property
    def mongodb_url(self) -> str:
        """SRV connection string.

        Credentials are percent-encoded so characters like @ : / # in the
        password cannot corrupt the URI.
        """
        username = quote_plus(self.mongodb_username)
        password = quote_plus(self.mongodb_password.get_secret_value())
        return f"mongodb+srv://{username}:{password}@{self.mongodb_host}"


settings = Settings()
