"""Gestión de cuentas (coordinación) y consulta de técnicos disponibles."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..dependencias import get_db, requiere_roles
from ..enums import Rol, TipoFalla
from ..errores import conflicto, no_encontrado
from ..models import Usuario
from ..schemas import (TecnicoDisponibilidad, UsuarioActualizar, UsuarioCrear, UsuarioSalida)
from ..seguridad import hashear_password
from ..servicios import trabajos_pendientes

router = APIRouter(tags=["Usuarios"])
solo_coordinacion = requiere_roles(Rol.COORDINACION)


@router.post("/usuarios", response_model=UsuarioSalida, status_code=201,
             summary="Crear una cuenta de cualquier perfil")
def crear_usuario(datos: UsuarioCrear, db: Session = Depends(get_db), _=Depends(solo_coordinacion)):
    if db.scalar(select(Usuario).where(Usuario.correo == datos.correo)):
        raise conflicto("Ya existe un usuario con ese correo")
    usuario = Usuario(nombre=datos.nombre, correo=datos.correo, telefono=datos.telefono,
                      password_hash=hashear_password(datos.password), rol=datos.rol, cargo=datos.cargo,
                      especialidades=[e.value for e in datos.especialidades],
                      experiencia_anios=datos.experiencia_anios)
    db.add(usuario)
    db.commit()
    return usuario


@router.get("/usuarios", response_model=list[UsuarioSalida], summary="Listar usuarios")
def listar_usuarios(rol: Rol | None = None, db: Session = Depends(get_db), _=Depends(solo_coordinacion)):
    consulta = select(Usuario).order_by(Usuario.nombre)
    if rol:
        consulta = consulta.where(Usuario.rol == rol)
    return db.scalars(consulta).all()


@router.get("/usuarios/{usuario_id}", response_model=UsuarioSalida, summary="Consultar un usuario")
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db), _=Depends(solo_coordinacion)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise no_encontrado("Usuario")
    return usuario


@router.patch("/usuarios/{usuario_id}", response_model=UsuarioSalida,
              summary="Actualizar datos, disponibilidad o estado de una cuenta")
def actualizar_usuario(usuario_id: int, datos: UsuarioActualizar, db: Session = Depends(get_db),
                       _=Depends(solo_coordinacion)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise no_encontrado("Usuario")
    cambios = datos.model_dump(exclude_unset=True)
    if "password" in cambios:
        usuario.password_hash = hashear_password(cambios.pop("password"))
    if "especialidades" in cambios:
        usuario.especialidades = [e.value for e in datos.especialidades or []]
        cambios.pop("especialidades")
    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)
    db.commit()
    return usuario


@router.get("/tecnicos", response_model=list[TecnicoDisponibilidad],
            summary="Técnicos con experiencia, disponibilidad y trabajos pendientes (apoyo a la asignación)")
def listar_tecnicos(tipo_falla: TipoFalla | None = None, db: Session = Depends(get_db),
                    _=Depends(solo_coordinacion)):
    tecnicos = db.scalars(select(Usuario).where(Usuario.rol == Rol.MANTENIMIENTO, Usuario.activo.is_(True))
                          .order_by(Usuario.nombre)).all()
    return [TecnicoDisponibilidad(
        id=t.id, nombre=t.nombre, especialidades=t.especialidades, experiencia_anios=t.experiencia_anios,
        disponible=t.disponible, trabajos_pendientes=trabajos_pendientes(db, t.id),
        coincide_especialidad=(tipo_falla.value in t.especialidades) if tipo_falla else None)
        for t in tecnicos]
