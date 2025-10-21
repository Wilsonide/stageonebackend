from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Config(BaseSettings):
    app_name: str = "FastAPI Application"
    db_url: str


config = Config()
