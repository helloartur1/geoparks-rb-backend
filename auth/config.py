from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import environ


env = environ.Env()
environ.Env.read_env('.env')


class AuthJWT(BaseModel):
    private_key_path: Path = Path(env('PATH_PRIVATE_KEY'))
    public_key_path: Path =  Path(env('PATH_PUBLIC_KEY'))
    algorithm: str = env('ALGORITHM')
    access_token_expire_minutes: int = int(env('ACCESS_TOKEN_EXPIRE_MINUTES'))


class Settings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()