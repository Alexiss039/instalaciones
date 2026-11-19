"""Configuración de la aplicación, leída de variables de entorno o del archivo .env."""
import secrets
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent  # carpeta backend/


class Configuracion(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    secret_key: str = ""
    token_minutos: int = 480
    database_url: str = f"sqlite:///{(BASE_DIR / 'instalaciones.db').as_posix()}"
    carpeta_subidas: str = "uploads"
    foto_max_mb: int = 5


configuracion = Configuracion()

# Sin SECRET_KEY configurada se genera una aleatoria (solo válida mientras corre el proceso).
if not configuracion.secret_key:
    configuracion.secret_key = secrets.token_urlsafe(48)


def ruta_subidas() -> Path:
    ruta = Path(configuracion.carpeta_subidas)
    if not ruta.is_absolute():
        ruta = BASE_DIR / ruta
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta
