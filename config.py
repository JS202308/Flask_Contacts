from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    sqlalchemy_uri: str = Field(env="SQLALCHEMY_URI")
    secret_key: str = Field(env="SECRET_KEY")
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()