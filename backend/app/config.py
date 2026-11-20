"""Configuración de la aplicación, leída de variables de entorno o del archivo .env."""
import secrets
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent  # carpeta backend/


class Configuracion(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    secret_key: str = ""
    token_minutos: int = 480
    database_url: str = f"sqlite:///{(BASE_DIR / 'instalaciones.db').as_posix()}"
    carpeta_subidas: str = "uploads"
    foto_max_mb: int = 5
    # Zona horaria de la organización: define qué día es "hoy" y los límites de los filtros
    # por fecha, sin depender de la zona del servidor (las marcas de tiempo se guardan en UTC).
    zona_horaria: str = "America/Bogota"


configuracion = Configuracion()

# Sin SECRET_KEY configurada se genera una aleatoria (solo válida mientras corre el proceso).
if not configuracion.secret_key:
    configuracion.secret_key = secrets.token_urlsafe(48)


def zona() -> ZoneInfo:
    """Zona horaria de la organización."""
    return ZoneInfo(configuracion.zona_horaria)


def hoy_local() -> date:
    """Fecha de hoy en la zona de la organización."""
    return datetime.now(zona()).date()


def inicio_dia_utc(dia: date, mas_dias: int = 0) -> datetime:
    """Medianoche local de `dia` (+ `mas_dias`), expresada en UTC sin zona, como se guarda en la base."""
    local = datetime.combine(dia + timedelta(days=mas_dias), time.min, tzinfo=zona())
    return local.astimezone(timezone.utc).replace(tzinfo=None)


def ruta_subidas() -> Path:
    ruta = Path(configuracion.carpeta_subidas)
    if not ruta.is_absolute():
        ruta = BASE_DIR / ruta
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta
