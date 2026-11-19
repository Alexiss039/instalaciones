"""Dashboard para coordinación: reportes por estado, fallas frecuentes, espacios y responsables, con filtro por fechas."""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..dependencias import get_db, requiere_roles
from ..enums import GRUPO_DE_ESTADO, EstadoReporte, Rol
from ..models import Asignacion, Edificio, Espacio, Reporte, Usuario
from ..schemas import Conteo, ResumenDashboard
from ..servicios import condiciones_fecha

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/resumen", response_model=ResumenDashboard,
            summary="Reportes por estado, fallas más frecuentes, espacios afectados y responsables")
def resumen(desde: date | None = None, hasta: date | None = None, db: Session = Depends(get_db),
            _=Depends(requiere_roles(Rol.COORDINACION))):
    condiciones = condiciones_fecha(desde, hasta)

    def agrupar(columna, *joins, filtros=()):
        consulta = select(columna, func.count().label("total")).select_from(Reporte)
        for destino, on in joins:
            consulta = consulta.join(destino, on)
        for c in (*condiciones, *filtros):
            consulta = consulta.where(c)
        return db.execute(consulta.group_by(columna).order_by(func.count().desc(), columna)).all()

    por_estado = agrupar(Reporte.estado)
    totales_grupo: dict[str, int] = {}
    for estado, total in por_estado:
        grupo = GRUPO_DE_ESTADO[estado].value
        totales_grupo[grupo] = totales_grupo.get(grupo, 0) + total

    espacios = db.execute(
        select(Espacio.id, Edificio.nombre, Espacio.nombre, func.count(Reporte.id).label("total"))
        .select_from(Reporte).join(Espacio, Reporte.espacio_id == Espacio.id)
        .join(Edificio, Espacio.edificio_id == Edificio.id)
        .where(*condiciones).group_by(Espacio.id, Edificio.nombre, Espacio.nombre)
        .order_by(func.count(Reporte.id).desc(), Espacio.id)).all()

    responsables = db.execute(
        select(Usuario.id, Usuario.nombre, func.count(func.distinct(Reporte.id)).label("total"))
        .select_from(Asignacion).join(Reporte, Asignacion.reporte_id == Reporte.id)
        .join(Usuario, Asignacion.tecnico_id == Usuario.id)
        .where(Asignacion.activa.is_(True), *condiciones).group_by(Usuario.id, Usuario.nombre)
        .order_by(func.count(func.distinct(Reporte.id)).desc(), Usuario.nombre)).all()

    resultados = agrupar(Reporte.resultado_cierre, filtros=(Reporte.resultado_cierre.is_not(None),))

    return ResumenDashboard(
        desde=desde, hasta=hasta, total_reportes=sum(t for _, t in por_estado),
        por_grupo=[Conteo(clave=g, etiqueta=g, total=t) for g, t in totales_grupo.items()],
        por_estado=[Conteo(clave=e.value, etiqueta=e.value, total=t) for e, t in por_estado],
        fallas_mas_frecuentes=[Conteo(clave=f.value, etiqueta=f.value, total=t)
                               for f, t in agrupar(Reporte.tipo_falla)],
        espacios_afectados=[Conteo(clave=str(i), etiqueta=f"{edificio} - {nombre}", total=t)
                            for i, edificio, nombre, t in espacios],
        por_responsable=[Conteo(clave=str(i), etiqueta=nombre, total=t) for i, nombre, t in responsables],
        por_resultado_cierre=[Conteo(clave=r.value, etiqueta=r.value, total=t) for r, t in resultados])
