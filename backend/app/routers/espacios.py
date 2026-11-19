"""Catálogo de edificios y espacios (consulta para todos; edición solo coordinación)."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..dependencias import get_db, requiere_roles, usuario_actual
from ..enums import Rol, TipoEspacio
from ..errores import conflicto, no_encontrado
from ..models import Edificio, Espacio
from ..schemas import (EdificioCrear, EdificioSalida, EspacioActualizar, EspacioCrear, EspacioSalida)

router = APIRouter(tags=["Espacios"])
solo_coordinacion = requiere_roles(Rol.COORDINACION)


@router.get("/edificios", response_model=list[EdificioSalida], summary="Listar edificios")
def listar_edificios(db: Session = Depends(get_db), _=Depends(usuario_actual)):
    return db.scalars(select(Edificio).order_by(Edificio.nombre)).all()


@router.post("/edificios", response_model=EdificioSalida, status_code=201, summary="Crear un edificio")
def crear_edificio(datos: EdificioCrear, db: Session = Depends(get_db), _=Depends(solo_coordinacion)):
    if db.scalar(select(Edificio).where(Edificio.nombre == datos.nombre)):
        raise conflicto("Ya existe un edificio con ese nombre")
    edificio = Edificio(**datos.model_dump())
    db.add(edificio)
    db.commit()
    return edificio


@router.get("/espacios", response_model=list[EspacioSalida], summary="Listar espacios")
def listar_espacios(edificio_id: int | None = None, tipo: TipoEspacio | None = None,
                    activo: bool | None = None, db: Session = Depends(get_db), _=Depends(usuario_actual)):
    consulta = select(Espacio).order_by(Espacio.edificio_id, Espacio.nombre)
    if edificio_id is not None:
        consulta = consulta.where(Espacio.edificio_id == edificio_id)
    if tipo:
        consulta = consulta.where(Espacio.tipo == tipo)
    if activo is not None:
        consulta = consulta.where(Espacio.activo.is_(activo))
    return db.scalars(consulta).unique().all()


@router.get("/espacios/{espacio_id}", response_model=EspacioSalida, summary="Consultar un espacio")
def obtener_espacio(espacio_id: int, db: Session = Depends(get_db), _=Depends(usuario_actual)):
    espacio = db.get(Espacio, espacio_id)
    if not espacio:
        raise no_encontrado("Espacio")
    return espacio


@router.post("/espacios", response_model=EspacioSalida, status_code=201, summary="Crear un espacio")
def crear_espacio(datos: EspacioCrear, db: Session = Depends(get_db), _=Depends(solo_coordinacion)):
    if not db.get(Edificio, datos.edificio_id):
        raise no_encontrado("Edificio")
    espacio = Espacio(**datos.model_dump())
    db.add(espacio)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise conflicto("Ya existe un espacio con ese nombre en el edificio")
    return espacio


@router.patch("/espacios/{espacio_id}", response_model=EspacioSalida,
              summary="Actualizar o desactivar un espacio")
def actualizar_espacio(espacio_id: int, datos: EspacioActualizar, db: Session = Depends(get_db),
                       _=Depends(solo_coordinacion)):
    espacio = db.get(Espacio, espacio_id)
    if not espacio:
        raise no_encontrado("Espacio")
    cambios = datos.model_dump(exclude_unset=True)
    if "edificio_id" in cambios and not db.get(Edificio, cambios["edificio_id"]):
        raise no_encontrado("Edificio")
    for campo, valor in cambios.items():
        setattr(espacio, campo, valor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise conflicto("Ya existe un espacio con ese nombre en el edificio")
    db.refresh(espacio)
    return espacio
