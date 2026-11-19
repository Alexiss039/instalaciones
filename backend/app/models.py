"""Modelo de datos (tablas)."""
from datetime import date, datetime, timezone

from sqlalchemy import (JSON, Boolean, Date, DateTime, Enum, ForeignKey, Integer,
                        String, Text, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .enums import (Cargo, EstadoReporte, Prioridad, ResultadoCierre, Rol, RolAsignacion,
                    TipoEspacio, TipoFalla)


def ahora() -> datetime:
    """Fecha y hora actual en UTC (sin zona, para guardar en la BD)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def col_enum(clase):
    return Enum(clase, native_enum=False, length=30, validate_strings=True,
                values_callable=lambda e: [x.value for x in e])


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    correo: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    telefono: Mapped[str] = mapped_column(String(30))
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[Rol] = mapped_column(col_enum(Rol))
    cargo: Mapped[Cargo | None] = mapped_column(col_enum(Cargo), nullable=True)
    especialidades: Mapped[list] = mapped_column(JSON, default=list)
    experiencia_anios: Mapped[int] = mapped_column(Integer, default=0)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=ahora)


class Edificio(Base):
    __tablename__ = "edificios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    espacios: Mapped[list["Espacio"]] = relationship(back_populates="edificio")


class Espacio(Base):
    __tablename__ = "espacios"
    __table_args__ = (UniqueConstraint("edificio_id", "nombre", name="uq_espacio_edificio_nombre"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    edificio_id: Mapped[int] = mapped_column(ForeignKey("edificios.id"))
    nombre: Mapped[str] = mapped_column(String(100))
    tipo: Mapped[TipoEspacio] = mapped_column(col_enum(TipoEspacio))
    piso: Mapped[str | None] = mapped_column(String(20), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    edificio: Mapped[Edificio] = relationship(back_populates="espacios", lazy="joined")


class Reporte(Base):
    __tablename__ = "reportes"

    id: Mapped[int] = mapped_column(primary_key=True)
    espacio_id: Mapped[int] = mapped_column(ForeignKey("espacios.id"), index=True)
    creado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    tipo_falla: Mapped[TipoFalla] = mapped_column(col_enum(TipoFalla), default=TipoFalla.OTRA)
    descripcion: Mapped[str] = mapped_column(Text)
    fecha_inicio_falla: Mapped[date] = mapped_column(Date)
    urgencia_reportada: Mapped[Prioridad | None] = mapped_column(col_enum(Prioridad), nullable=True)
    estado: Mapped[EstadoReporte] = mapped_column(col_enum(EstadoReporte),
                                                  default=EstadoReporte.REPORTADO, index=True)

    # Evaluación
    prioridad: Mapped[Prioridad | None] = mapped_column(col_enum(Prioridad), nullable=True)
    requiere_verificacion: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicado_de_id: Mapped[int | None] = mapped_column(ForeignKey("reportes.id"), nullable=True)
    motivo_rechazo: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    fecha_evaluacion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Cierre
    resultado_cierre: Mapped[ResultadoCierre | None] = mapped_column(col_enum(ResultadoCierre), nullable=True)
    descripcion_solucion: Mapped[str | None] = mapped_column(Text, nullable=True)
    motivo_cierre: Mapped[str | None] = mapped_column(Text, nullable=True)
    finalizado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    verificado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    fecha_cierre: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    creado_en: Mapped[datetime] = mapped_column(DateTime, default=ahora, index=True)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime, default=ahora, onupdate=ahora)

    espacio: Mapped[Espacio] = relationship(lazy="joined")
    creador: Mapped[Usuario] = relationship(foreign_keys=[creado_por_id], lazy="joined")
    fotos: Mapped[list["Foto"]] = relationship(back_populates="reporte", order_by="Foto.id")
    asignaciones: Mapped[list["Asignacion"]] = relationship(back_populates="reporte", order_by="Asignacion.id")
    intervenciones: Mapped[list["Intervencion"]] = relationship(back_populates="reporte",
                                                                order_by="Intervencion.id")
    historial: Mapped[list["HistorialEstado"]] = relationship(back_populates="reporte",
                                                              order_by="HistorialEstado.id")
    valoraciones: Mapped[list["ValoracionTecnica"]] = relationship(back_populates="reporte",
                                                                   order_by="ValoracionTecnica.id")


class Foto(Base):
    __tablename__ = "fotos"

    id: Mapped[int] = mapped_column(primary_key=True)
    reporte_id: Mapped[int] = mapped_column(ForeignKey("reportes.id"), index=True)
    nombre_archivo: Mapped[str] = mapped_column(String(80))
    nombre_original: Mapped[str] = mapped_column(String(200))
    tipo_contenido: Mapped[str] = mapped_column(String(50))
    tamano_bytes: Mapped[int] = mapped_column(Integer)
    subido_en: Mapped[datetime] = mapped_column(DateTime, default=ahora)

    reporte: Mapped[Reporte] = relationship(back_populates="fotos")


class HistorialEstado(Base):
    __tablename__ = "historial_estados"

    id: Mapped[int] = mapped_column(primary_key=True)
    reporte_id: Mapped[int] = mapped_column(ForeignKey("reportes.id"), index=True)
    estado_anterior: Mapped[EstadoReporte | None] = mapped_column(col_enum(EstadoReporte), nullable=True)
    estado_nuevo: Mapped[EstadoReporte] = mapped_column(col_enum(EstadoReporte))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=ahora)

    reporte: Mapped[Reporte] = relationship(back_populates="historial")
    usuario: Mapped[Usuario] = relationship(lazy="joined")


class ValoracionTecnica(Base):
    """Apoyo que coordinación solicita a mantenimiento antes de evaluar."""
    __tablename__ = "valoraciones_tecnicas"

    id: Mapped[int] = mapped_column(primary_key=True)
    reporte_id: Mapped[int] = mapped_column(ForeignKey("reportes.id"), index=True)
    tecnico_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    solicitada_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    indicaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime, default=ahora)
    concepto: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_respuesta: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    reporte: Mapped[Reporte] = relationship(back_populates="valoraciones")
    tecnico: Mapped[Usuario] = relationship(foreign_keys=[tecnico_id], lazy="joined")


class Asignacion(Base):
    __tablename__ = "asignaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    reporte_id: Mapped[int] = mapped_column(ForeignKey("reportes.id"), index=True)
    tecnico_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    asignado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    rol: Mapped[RolAsignacion] = mapped_column(col_enum(RolAsignacion), default=RolAsignacion.RESPONSABLE)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_asignacion: Mapped[datetime] = mapped_column(DateTime, default=ahora)
    fecha_retiro: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    motivo_retiro: Mapped[str | None] = mapped_column(Text, nullable=True)

    reporte: Mapped[Reporte] = relationship(back_populates="asignaciones")
    tecnico: Mapped[Usuario] = relationship(foreign_keys=[tecnico_id], lazy="joined")


class Intervencion(Base):
    __tablename__ = "intervenciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    reporte_id: Mapped[int] = mapped_column(ForeignKey("reportes.id"), index=True)
    tecnico_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    fecha_intervencion: Mapped[date] = mapped_column(Date)
    actividades: Mapped[str] = mapped_column(Text)
    tiempo_minutos: Mapped[int] = mapped_column(Integer)
    resultado: Mapped[str] = mapped_column(Text)
    registrado_en: Mapped[datetime] = mapped_column(DateTime, default=ahora)

    reporte: Mapped[Reporte] = relationship(back_populates="intervenciones")
    tecnico: Mapped[Usuario] = relationship(foreign_keys=[tecnico_id], lazy="joined")
