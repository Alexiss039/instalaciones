"""Registro de reportantes e inicio de sesión."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..dependencias import get_db, usuario_actual
from ..enums import Rol
from ..errores import conflicto
from ..models import Usuario
from ..schemas import RegistroReportante, TokenSalida, UsuarioSalida
from ..seguridad import crear_token, hashear_password, verificar_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioSalida, status_code=201,
             summary="Registro de un docente o administrativo (perfil reportante)")
def registrar(datos: RegistroReportante, db: Session = Depends(get_db)):
    if db.scalar(select(Usuario).where(Usuario.correo == datos.correo)):
        raise conflicto("Ya existe un usuario con ese correo")
    usuario = Usuario(nombre=datos.nombre, correo=datos.correo, telefono=datos.telefono,
                      password_hash=hashear_password(datos.password), rol=Rol.REPORTANTE,
                      cargo=datos.cargo)
    db.add(usuario)
    db.commit()
    return usuario


@router.post("/login", response_model=TokenSalida, summary="Inicio de sesión (usuario = correo)")
def login(formulario: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.scalar(select(Usuario).where(Usuario.correo == formulario.username.strip().lower()))
    if not usuario or not verificar_password(formulario.password, usuario.password_hash):
        raise HTTPException(401, "Correo o contraseña incorrectos")
    if not usuario.activo:
        raise HTTPException(403, "La cuenta está desactivada")
    return TokenSalida(access_token=crear_token(usuario.id), usuario=usuario)


@router.get("/yo", response_model=UsuarioSalida, summary="Datos del usuario autenticado")
def yo(usuario: Usuario = Depends(usuario_actual)):
    return usuario
