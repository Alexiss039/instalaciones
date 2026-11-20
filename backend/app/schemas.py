"""Esquemas de entrada y salida de la API (validaciones con Pydantic)."""
from datetime import date, datetime
from typing import Annotated

from pydantic import (BaseModel, ConfigDict, Field, StringConstraints, computed_field,
                      field_validator, model_validator)

from .config import hoy_local
from .enums import (GRUPO_DE_ESTADO, Cargo, DecisionEvaluacion, EstadoReporte, GrupoEstado,
                    Prioridad, ResultadoCierre, Rol, RolAsignacion, TipoEspacio, TipoFalla)

Texto = Annotated[str, StringConstraints(strip_whitespace=True)]
Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=120)]
Correo = Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True, max_length=160,
                                          pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]
Telefono = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[0-9+\- ()]{7,20}$")]
Password = Annotated[str, StringConstraints(min_length=8, max_length=72)]


def _no_futura(v: date) -> date:
    if v > hoy_local():
        raise ValueError("La fecha no puede ser futura")
    return v


def _password_segura(v: str) -> str:
    if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
        raise ValueError("La contraseña debe tener al menos una letra y un número")
    return v


class Salida(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------- Usuarios
class RegistroReportante(BaseModel):
    nombre: Nombre
    correo: Correo
    telefono: Telefono
    password: Password
    cargo: Cargo

    _v = field_validator("password")(_password_segura)


class UsuarioCrear(BaseModel):
    nombre: Nombre
    correo: Correo
    telefono: Telefono
    password: Password
    rol: Rol
    cargo: Cargo | None = None
    especialidades: list[TipoFalla] = []
    experiencia_anios: int = Field(0, ge=0, le=60)

    _v = field_validator("password")(_password_segura)

    @model_validator(mode="after")
    def _coherencia(self):
        if self.rol == Rol.REPORTANTE and self.cargo is None:
            raise ValueError("El cargo (docente/administrativo) es obligatorio para un reportante")
        return self


class UsuarioActualizar(BaseModel):
    nombre: Nombre | None = None
    telefono: Telefono | None = None
    cargo: Cargo | None = None
    especialidades: list[TipoFalla] | None = None
    experiencia_anios: int | None = Field(None, ge=0, le=60)
    disponible: bool | None = None
    activo: bool | None = None
    password: Password | None = None

    @field_validator("password")
    @classmethod
    def _p(cls, v):
        return _password_segura(v) if v is not None else v


class UsuarioSalida(Salida):
    id: int
    nombre: str
    correo: str
    telefono: str
    rol: Rol
    cargo: Cargo | None
    especialidades: list[str]
    experiencia_anios: int
    disponible: bool
    activo: bool


class UsuarioContacto(Salida):
    id: int
    nombre: str
    correo: str
    telefono: str
    cargo: Cargo | None


class UsuarioBasico(Salida):
    id: int
    nombre: str


class TokenSalida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioSalida


class TecnicoDisponibilidad(BaseModel):
    id: int
    nombre: str
    especialidades: list[str]
    experiencia_anios: int
    disponible: bool
    trabajos_pendientes: int
    coincide_especialidad: bool | None = None


# ---------------------------------------------------------------- Espacios
class EdificioCrear(BaseModel):
    nombre: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]
    descripcion: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)] | None = None


class EdificioSalida(Salida):
    id: int
    nombre: str
    descripcion: str | None


class EspacioCrear(BaseModel):
    edificio_id: int
    nombre: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]
    tipo: TipoEspacio
    piso: Annotated[str, StringConstraints(strip_whitespace=True, max_length=20)] | None = None


class EspacioActualizar(BaseModel):
    edificio_id: int | None = None
    nombre: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)] | None = None
    tipo: TipoEspacio | None = None
    piso: Annotated[str, StringConstraints(strip_whitespace=True, max_length=20)] | None = None
    activo: bool | None = None


class EspacioSalida(Salida):
    id: int
    nombre: str
    tipo: TipoEspacio
    piso: str | None
    activo: bool
    edificio: EdificioSalida


# ---------------------------------------------------------------- Reportes
class ReporteCrear(BaseModel):
    espacio_id: int
    descripcion: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=1000)]
    fecha_inicio_falla: date
    tipo_falla: TipoFalla = TipoFalla.OTRA
    urgencia_reportada: Prioridad | None = None

    _v = field_validator("fecha_inicio_falla")(_no_futura)


class FotoSalida(Salida):
    id: int
    nombre_original: str
    tipo_contenido: str
    tamano_bytes: int
    subido_en: datetime


class HistorialSalida(Salida):
    id: int
    estado_anterior: EstadoReporte | None
    estado_nuevo: EstadoReporte
    usuario: UsuarioBasico
    comentario: str | None
    fecha: datetime


class AsignacionSalida(Salida):
    id: int
    tecnico: UsuarioBasico
    rol: RolAsignacion
    activa: bool
    motivo: str | None
    fecha_asignacion: datetime
    fecha_retiro: datetime | None
    motivo_retiro: str | None


class IntervencionSalida(Salida):
    id: int
    tecnico: UsuarioBasico
    fecha_intervencion: date
    actividades: str
    tiempo_minutos: int
    resultado: str
    registrado_en: datetime


class ValoracionSalida(Salida):
    id: int
    tecnico: UsuarioBasico
    indicaciones: str | None
    fecha_solicitud: datetime
    concepto: str | None
    fecha_respuesta: datetime | None


class ReportanteSalida(BaseModel):
    usuario: UsuarioContacto
    reporte_id: int
    fecha_reporte: datetime
    es_reporte_original: bool


class ReporteResumen(Salida):
    id: int
    espacio: EspacioSalida
    tipo_falla: TipoFalla
    descripcion: str
    fecha_inicio_falla: date
    estado: EstadoReporte
    prioridad: Prioridad | None
    duplicado_de_id: int | None
    creado_en: datetime
    creador: UsuarioBasico

    @computed_field
    @property
    def grupo(self) -> GrupoEstado:
        return GRUPO_DE_ESTADO[self.estado]


class ReporteDetalle(ReporteResumen):
    urgencia_reportada: Prioridad | None
    requiere_verificacion: bool
    motivo_rechazo: str | None
    resultado_cierre: ResultadoCierre | None
    descripcion_solucion: str | None
    motivo_cierre: str | None
    fecha_cierre: datetime | None
    creador: UsuarioContacto
    fotos: list[FotoSalida]
    asignaciones: list[AsignacionSalida]
    intervenciones: list[IntervencionSalida]
    historial: list[HistorialSalida]
    valoraciones: list[ValoracionSalida]
    # Los siguientes campos se completan en el servicio según el perfil de quien consulta
    reportantes: list[ReportanteSalida] = []
    estado_reporte_original: EstadoReporte | None = None


class EvaluacionEntrada(BaseModel):
    decision: DecisionEvaluacion
    corresponde_instalaciones: bool = True
    informacion_suficiente: bool = True
    prioridad: Prioridad | None = None
    requiere_verificacion: bool | None = None
    motivo: Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=500)] | None = None
    duplicado_de_id: int | None = None

    @model_validator(mode="after")
    def _segun_decision(self):
        if self.decision == DecisionEvaluacion.ACEPTAR:
            if self.prioridad is None:
                raise ValueError("Para aceptar un reporte debe definir la prioridad")
            if not self.corresponde_instalaciones:
                raise ValueError("No se puede aceptar una falla que no corresponde a las instalaciones")
            if not self.informacion_suficiente:
                raise ValueError("No se puede aceptar un reporte con información insuficiente")
        elif self.decision == DecisionEvaluacion.RECHAZAR and not self.motivo:
            raise ValueError("Para rechazar un reporte debe indicar el motivo")
        elif self.decision == DecisionEvaluacion.DUPLICADO and self.duplicado_de_id is None:
            raise ValueError("Para marcar un duplicado debe indicar el reporte original (duplicado_de_id)")
        return self


class ValoracionCrear(BaseModel):
    tecnico_id: int
    indicaciones: Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)] | None = None


class ValoracionResponder(BaseModel):
    concepto: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=1000)]


class AsignacionCrear(BaseModel):
    tecnico_id: int
    rol: RolAsignacion = RolAsignacion.RESPONSABLE
    motivo: Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)] | None = None


class AsignacionRetirar(BaseModel):
    motivo: Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=500)]


class IntervencionCrear(BaseModel):
    fecha_intervencion: date
    actividades: Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=2000)]
    tiempo_minutos: int = Field(ge=1, le=1440)
    resultado: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=1000)]

    _v = field_validator("fecha_intervencion")(_no_futura)


class FinalizarEntrada(BaseModel):
    resultado: ResultadoCierre
    descripcion_solucion: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10,
                                                           max_length=2000)]
    motivo: Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=500)] | None = None

    @model_validator(mode="after")
    def _motivo(self):
        if self.resultado != ResultadoCierre.RESUELTO and not self.motivo:
            raise ValueError("Cuando la falla no queda resuelta debe indicar el motivo")
        return self


class VerificarEntrada(BaseModel):
    aprobado: bool
    comentario: Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=500)] | None = None

    @model_validator(mode="after")
    def _comentario(self):
        if not self.aprobado and not self.comentario:
            raise ValueError("Si no aprueba el cierre debe indicar el motivo en 'comentario'")
        return self


# ---------------------------------------------------------------- Dashboard
class Conteo(BaseModel):
    clave: str
    etiqueta: str
    total: int


class ResumenDashboard(BaseModel):
    desde: date | None
    hasta: date | None
    total_reportes: int
    por_grupo: list[Conteo]
    por_estado: list[Conteo]
    fallas_mas_frecuentes: list[Conteo]
    espacios_afectados: list[Conteo]
    por_responsable: list[Conteo]
    por_resultado_cierre: list[Conteo]
