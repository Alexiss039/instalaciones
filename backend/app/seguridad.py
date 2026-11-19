"""Hash de contraseñas (PBKDF2 de la biblioteca estándar) y tokens JWT."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from .config import configuracion

ITERACIONES = 240_000
ALGORITMO = "HS256"


def hashear_password(password: str) -> str:
    sal = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), sal.encode(), ITERACIONES).hex()
    return f"pbkdf2_sha256${ITERACIONES}${sal}${h}"


def verificar_password(password: str, almacenado: str) -> bool:
    try:
        _, iteraciones, sal, h = almacenado.split("$")
        calculado = hashlib.pbkdf2_hmac("sha256", password.encode(), sal.encode(), int(iteraciones)).hex()
        return hmac.compare_digest(calculado, h)
    except (ValueError, AttributeError):
        return False


def crear_token(usuario_id: int) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=configuracion.token_minutos)
    return jwt.encode({"sub": str(usuario_id), "exp": expira}, configuracion.secret_key, algorithm=ALGORITMO)


def leer_token(token: str) -> int | None:
    try:
        datos = jwt.decode(token, configuracion.secret_key, algorithms=[ALGORITMO])
        return int(datos["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
