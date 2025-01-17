from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = "postgresql+asyncpg://postgres:111111@localhost:5432/abc"
    secret_key: str = "1234567890"
    algorithm: str = "HS256"
    mail_username: str = "example@mail.com"
    mail_password: str = "password"
    mail_from: str = "example@mail.com"
    mail_port: int = 567234
    mail_server: str = "mail"
    redis_host: str = "localhost"
    redis_port: int = 6379
    cloudinary_name: str = "name"
    cloudinary_api_key: str = "000000000000000"
    cloudinary_api_secret: str = "secret"

    class Config:
        extra = "ignore"
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
