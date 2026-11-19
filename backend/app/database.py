"""Conexión a la base de datos (SQLAlchemy)."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import configuracion


class Base(DeclarativeBase):
    pass


def crear_motor(url: str, **kwargs):
    argumentos = {"check_same_thread": False} if url.startswith("sqlite") else {}
    motor = create_engine(url, connect_args=argumentos, **kwargs)
    if url.startswith("sqlite"):
        @event.listens_for(motor, "connect")
        def _activar_llaves_foraneas(conexion, _):
            conexion.execute("PRAGMA foreign_keys=ON")
    return motor


motor = crear_motor(configuracion.database_url)
SesionLocal = sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)


def crear_tablas(m=None):
    from . import models  # noqa: F401  (registra los modelos)
    Base.metadata.create_all(bind=m or motor)
