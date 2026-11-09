from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "dev"
    port: int = 8000
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 60
    hash_scheme: str = "argon2id"
    argon2_time_cost: int = 3
    argon2_memory_cost: int = 65536
    argon2_parallelism: int = 2


settings = Settings()
