"""Application config."""

from dataclasses import dataclass
import os


@dataclass
class Config:
    """Application configuration object."""

    root_path: str = os.getenv("API_ROOT_PATH", default="")

    # configuration values come from /docker-compose.yml
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", 5432))
    db_name: str = os.getenv("DB_NAME", "finance")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")

    @property
    def database_url(self) -> str: # Constructs full database connection string
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
