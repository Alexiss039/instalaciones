"""Reglas de negocio: transiciones de estado, visibilidad por perfil y consultas."""
from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .config import inicio_dia_utc
from .enums import EstadoReporte as E
from .enums import Rol
from .errores import conflicto, no_encontrado, prohibido, regla_negocio
from .models import Asignacion, HistorialEstado, Reporte, Usuario, ValoracionTecnica
from .schemas import ReporteDetalle, ReportanteSalida

# Transiciones permitidas entre estados (cualquier otra se rechaza con 409)
TRANSICIONES: dict[E, set[E]] = {
    E.REPORTADO: {E.EVALUADO, E.RECHAZADO, E.DUPLICADO},
    E.EVALUADO: {E.ASIGNADO},
    E.ASIGNADO: {E.EN_ATENCION},
    E.EN_ATENCION: {E.EN_VERIFICACION, E.CERRADO},
    E.EN_VERIFICACION: {E.CERRADO, E.EN_ATENCION},
    E.CERRADO: set(),
    E.RECHAZADO: set(),
    E.DUPLICADO: set(),
}


def cambiar_estado(db: Session, reporte: Reporte, nuevo: E, usuario: Usuario,
                   comentario: str | None = None) -> None:
    """Aplica una transición validando que esté permitida y deja rastro en el historial."""
    if nuevo not in TRANSICIONES[reporte.estado]:
        raise conflicto(f"Transición no permitida: de '{reporte.estado.value}' a '{nuevo.value}'")
    db.add(HistorialEstado(reporte=reporte, estado_anterior=reporte.estado, estado_nuevo=nuevo,
                           usuario_id=usuario.id, comentario=comentario))
    reporte.estado = nuevo


def exigir_estado(reporte: Reporte, *permitidos: E, accion: str) -> None:
    if reporte.estado not in permitidos:
        lista = ", ".join(e.value for e in permitidos)
        raise conflicto(f"No se puede {accion} un reporte en estado '{reporte.estado.value}' "
                        f"(estados válidos: {lista})")


def asignaciones_activas(reporte: Reporte) -> list[Asignacion]:
    return [a for a in reporte.asignaciones if a.activa]


def es_tecnico_asignado(reporte: Reporte, usuario: Usuario) -> bool:
    return any(a.tecnico_id == usuario.id for a in asignaciones_activas(reporte))


def responsable_activo(reporte: Reporte) -> Asignacion | None:
    return next((a for a in asignaciones_activas(reporte) if a.rol.value == "responsable"), None)


def tiene_valoracion(reporte: Reporte, usuario: Usuario) -> bool:
    return any(v.tecnico_id == usuario.id for v in reporte.valoraciones)


def puede_ver(usuario: Usuario, reporte: Reporte) -> bool:
    if usuario.rol == Rol.COORDINACION:
        return True
    if usuario.rol == Rol.REPORTANTE:
        return reporte.creado_por_id == usuario.id
    return es_tecnico_asignado(reporte, usuario) or tiene_valoracion(reporte, usuario)


def filtro_visibilidad(usuario: Usuario):
    """Condición SQL equivalente a puede_ver, para los listados."""
    if usuario.rol == Rol.COORDINACION:
        return None
    if usuario.rol == Rol.REPORTANTE:
        return Reporte.creado_por_id == usuario.id
    asignado = select(Asignacion.reporte_id).where(Asignacion.tecnico_id == usuario.id,
                                                   Asignacion.activa.is_(True))
    valorando = select(ValoracionTecnica.reporte_id).where(ValoracionTecnica.tecnico_id == usuario.id)
    return or_(Reporte.id.in_(asignado), Reporte.id.in_(valorando))


def obtener_reporte(db: Session, reporte_id: int, usuario: Usuario) -> Reporte:
    """Devuelve el reporte si existe y el usuario puede verlo (404 si no existe, 403 si no es suyo)."""
    reporte = db.get(Reporte, reporte_id)
    if not reporte:
        raise no_encontrado("Reporte")
    if not puede_ver(usuario, reporte):
        raise prohibido("No tiene acceso a este reporte")
    return reporte


def reportantes_de(db: Session, reporte: Reporte) -> list[ReportanteSalida]:
    """Quien reportó originalmente más quienes reportaron lo mismo (reportes duplicados vinculados)."""
    duplicados = db.scalars(select(Reporte).where(Reporte.duplicado_de_id == reporte.id)
                            .order_by(Reporte.id)).all()
    lista = [ReportanteSalida(usuario=reporte.creador, reporte_id=reporte.id,
                              fecha_reporte=reporte.creado_en, es_reporte_original=True)]
    lista += [ReportanteSalida(usuario=d.creador, reporte_id=d.id, fecha_reporte=d.creado_en,
                               es_reporte_original=False) for d in duplicados]
    return lista


def construir_detalle(db: Session, reporte: Reporte, usuario: Usuario) -> ReporteDetalle:
    detalle = ReporteDetalle.model_validate(reporte)
    if usuario.rol != Rol.REPORTANTE:  # el reportante no ve datos de otras personas
        detalle.reportantes = reportantes_de(db, reporte)
    if reporte.duplicado_de_id:
        original = db.get(Reporte, reporte.duplicado_de_id)
        detalle.estado_reporte_original = original.estado if original else None
    return detalle


def condiciones_fecha(desde: date | None, hasta: date | None) -> list:
    """Filtro por fecha de creación del reporte; 'hasta' incluye todo ese día.

    Las fechas son días de la zona de la organización y `creado_en` se guarda en UTC, así que
    los límites se convierten a UTC antes de comparar.
    """
    if desde and hasta and desde > hasta:
        raise regla_negocio("La fecha 'desde' no puede ser posterior a 'hasta'")
    condiciones = []
    if desde:
        condiciones.append(Reporte.creado_en >= inicio_dia_utc(desde))
    if hasta:
        condiciones.append(Reporte.creado_en < inicio_dia_utc(hasta, 1))
    return condiciones


def trabajos_pendientes(db: Session, tecnico_id: int) -> int:
    """Reportes no finalizados en los que el técnico tiene una asignación activa."""
    finalizados = (E.CERRADO, E.RECHAZADO, E.DUPLICADO)
    return len(set(db.scalars(
        select(Asignacion.reporte_id).join(Reporte)
        .where(Asignacion.tecnico_id == tecnico_id, Asignacion.activa.is_(True),
               Reporte.estado.not_in(finalizados))).all()))
