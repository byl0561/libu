"""Runtime configuration (env-driven). No JWT/auth — access control is nginx Basic Auth."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LIBU_", env_file=".env", extra="ignore")

    # SQLite file location. In the container this lives on the mounted data volume.
    data_dir: str = "./data"
    db_filename: str = "libu.db"

    # Comma-separated CORS origins; "*" by default since the app is same-origin behind nginx.
    cors_origins: str = "*"

    # Seeded on first boot so the "记账人" dropdown is never empty.
    default_members: str = "我"

    @property
    def database_url(self) -> str:
        db_path = Path(self.data_dir) / self.db_filename
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
