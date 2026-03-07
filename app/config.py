from pydantic_settings import BaseSettings

class Config(BaseSettings):
    database_api: str


config = Config()
