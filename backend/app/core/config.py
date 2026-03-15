from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Moodle Journal API"
    app_env: str = "dev"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24

    postgres_db: str = "moodle_journal"
    postgres_user: str = "moodle"
    postgres_password: str = "moodle"
    postgres_host: str = "db"
    postgres_port: int = 5432

    moodle_base_url: str = "http://moodle.local"
    moodle_token: str = ""

    moodle_sync_mode: str = "demo"
    moodle_timeout_seconds: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
