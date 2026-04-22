"""Application configuration via environment variables."""

import os


class Settings:

    def __init__(self):
        self.mongo_uri: str = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
        self.mongo_db_name: str = os.getenv("MONGO_DB_NAME", "http_metadata")
        self.request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.app_host: str = os.getenv("APP_HOST", "0.0.0.0")
        self.app_port: int = int(os.getenv("APP_PORT", "8000"))


settings = Settings()
