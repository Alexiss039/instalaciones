"""Catálogos y estados del sistema."""
from enum import Enum


class Rol(str, Enum):
    REPORTANTE = "reportante"
    MANTENIMIENTO = "mantenimiento"
    COORDINACION = "coordinacion"


class Cargo(str, Enum):
    DOCENTE = "docente"
    ADMINISTRATIVO = "administrativo"


class TipoEspacio(str, Enum):
    AULA = "aula"
    OFICINA = "oficina"
    LABORATORIO = "laboratorio"
    ZONA_COMUN = "zona_comun"
    OTRO = "otro"


class TipoFalla(str, Enum):
    ELECTRICA = "electrica"
    ILUMINACION = "iluminacion"
    PLOMERIA = "plomeria"
    CLIMATIZACION = "climatizacion"
    MOBILIARIO = "mobiliario"
    RED_DATOS = "red_datos"
    ESTRUCTURA = "estructura"
    OTRA = "otra"


class Prioridad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class EstadoReporte(str, Enum):
    REPORTADO = "reportado"
    EVALUADO = "evaluado"
    ASIGNADO = "asignado"
    EN_ATENCION = "en_atencion"
    EN_VERIFICACION = "en_verificacion"
    CERRADO = "cerrado"
    RECHAZADO = "rechazado"
    DUPLICADO = "duplicado"


class GrupoEstado(str, Enum):
    PENDIENTE = "pendiente"
    EN_ATENCION = "en_atencion"
    FINALIZADO = "finalizado"


GRUPO_DE_ESTADO = {
    EstadoReporte.REPORTADO: GrupoEstado.PENDIENTE,
    EstadoReporte.EVALUADO: GrupoEstado.PENDIENTE,
    EstadoReporte.ASIGNADO: GrupoEstado.PENDIENTE,
    EstadoReporte.EN_ATENCION: GrupoEstado.EN_ATENCION,
    EstadoReporte.EN_VERIFICACION: GrupoEstado.EN_ATENCION,
    EstadoReporte.CERRADO: GrupoEstado.FINALIZADO,
    EstadoReporte.RECHAZADO: GrupoEstado.FINALIZADO,
    EstadoReporte.DUPLICADO: GrupoEstado.FINALIZADO,
}


def estados_del_grupo(grupo: GrupoEstado) -> list[EstadoReporte]:
    return [e for e, g in GRUPO_DE_ESTADO.items() if g == grupo]


class DecisionEvaluacion(str, Enum):
    ACEPTAR = "aceptar"
    RECHAZAR = "rechazar"
    DUPLICADO = "duplicado"


class ResultadoCierre(str, Enum):
    RESUELTO = "resuelto"
    NO_REPRODUCIBLE = "no_reproducible"
    REQUIERE_TERCERO = "requiere_tercero"
    NO_SOLUCIONABLE = "no_solucionable"


class RolAsignacion(str, Enum):
    RESPONSABLE = "responsable"
    APOYO = "apoyo"
