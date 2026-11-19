"""Dependencias de FastAPI: sesión de BD, usuario autenticado y control de roles."""
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import database
from .enums import Rol
from .errores import prohibido
from .models import Usuario
from .seguridad import leer_token

esquema_oauth = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_db():
    db = database.SesionLocal()
    try:
        yield db
    finally:
        db.close()


def usuario_actual(token: str | None = Depends(esquema_oauth), db: Session = Depends(get_db)) -> Usuario:
    no_autenticado = HTTPException(401, "Credenciales no válidas o sesión expirada",
                                   headers={"WWW-Authenticate": "Bearer"})
    if not token:
        raise no_autenticado
    usuario_id = leer_token(token)
    usuario = db.get(Usuario, usuario_id) if usuario_id else None
    if not usuario or not usuario.activo:
        raise no_autenticado
    return usuario


def requiere_roles(*roles: Rol):
    def verificar(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
        if usuario.rol not in roles:
            raise prohibido("Su perfil no tiene permiso para realizar esta acción")
        return usuario
    return verificar
