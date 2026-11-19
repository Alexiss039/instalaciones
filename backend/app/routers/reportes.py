"""Ciclo de vida del reporte: registro, evaluación, asignación, intervención y cierre."""
import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import configuracion, ruta_subidas
from ..dependencias import get_db, requiere_roles, usuario_actual
from ..enums import (DecisionEvaluacion, EstadoReporte as E, GrupoEstado, Prioridad,
                     ResultadoCierre, Rol, RolAsignacion, TipoFalla, estados_del_grupo)
from ..errores import conflicto, no_encontrado, prohibido, regla_negocio
from ..models import (Asignacion, Espacio, Foto, HistorialEstado, Intervencion, Reporte, Usuario,
                      ValoracionTecnica, ahora)
from ..schemas import (AsignacionCrear, AsignacionRetirar, AsignacionSalida, EvaluacionEntrada,
                       FinalizarEntrada, FotoSalida, HistorialSalida, IntervencionCrear,
                       IntervencionSalida, ReporteCrear, ReporteDetalle, ReporteResumen,
                       ValoracionCrear, ValoracionResponder, ValoracionSalida, VerificarEntrada)
from ..servicios import (asignaciones_activas, cambiar_estado, condiciones_fecha,
                         construir_detalle, es_tecnico_asignado, exigir_estado, filtro_visibilidad,
                         obtener_reporte, responsable_activo, tiene_valoracion)

router = APIRouter(prefix="/reportes", tags=["Reportes"])
solo_coordinacion = requiere_roles(Rol.COORDINACION)
solo_reportante = requiere_roles(Rol.REPORTANTE)
solo_mantenimiento = requiere_roles(Rol.MANTENIMIENTO)

MAX_FOTOS = 5
FIRMAS_IMAGEN = {"image/jpeg": b"\xff\xd8\xff", "image/png": b"\x89PNG\r\n\x1a\n", "image/webp": b"RIFF"}
EXTENSIONES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


# ------------------------------------------------------------ Registro y consulta
@router.post("", response_model=ReporteDetalle, status_code=201,
             summary="Registrar una falla (docentes y administrativos)")
def crear_reporte(datos: ReporteCrear, db: Session = Depends(get_db),
                  usuario: Usuario = Depends(solo_reportante)):
    espacio = db.get(Espacio, datos.espacio_id)
    if not espacio or not espacio.activo:
        raise regla_negocio("El espacio indicado no existe o está inactivo")
    reporte = Reporte(espacio_id=espacio.id, creado_por_id=usuario.id, tipo_falla=datos.tipo_falla,
                      descripcion=datos.descripcion, fecha_inicio_falla=datos.fecha_inicio_falla,
                      urgencia_reportada=datos.urgencia_reportada, estado=E.REPORTADO)
    db.add(reporte)
    db.flush()
    db.add(HistorialEstado(reporte_id=reporte.id, estado_anterior=None, estado_nuevo=E.REPORTADO,
                           usuario_id=usuario.id, comentario="Reporte registrado"))
    db.commit()
    db.refresh(reporte)
    return construir_detalle(db, reporte, usuario)


@router.get("", response_model=list[ReporteResumen],
            summary="Listar reportes (cada perfil ve solo los que le corresponden)")
def listar_reportes(estado: E | None = None, grupo: GrupoEstado | None = None,
                    espacio_id: int | None = None, tipo_falla: TipoFalla | None = None,
                    prioridad: Prioridad | None = None, tecnico_id: int | None = None,
                    desde: date | None = None, hasta: date | None = None,
                    limite: int = Query(50, ge=1, le=200), desplazamiento: int = Query(0, ge=0),
                    db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_actual)):
    consulta = select(Reporte).order_by(Reporte.id.desc())
    visibilidad = filtro_visibilidad(usuario)
    if visibilidad is not None:
        consulta = consulta.where(visibilidad)
    if estado:
        consulta = consulta.where(Reporte.estado == estado)
    if grupo:
        consulta = consulta.where(Reporte.estado.in_(estados_del_grupo(grupo)))
    if espacio_id is not None:
        consulta = consulta.where(Reporte.espacio_id == espacio_id)
    if tipo_falla:
        consulta = consulta.where(Reporte.tipo_falla == tipo_falla)
    if prioridad:
        consulta = consulta.where(Reporte.prioridad == prioridad)
    if tecnico_id is not None:
        consulta = consulta.where(Reporte.id.in_(
            select(Asignacion.reporte_id).where(Asignacion.tecnico_id == tecnico_id,
                                                Asignacion.activa.is_(True))))
    for condicion in condiciones_fecha(desde, hasta):
        consulta = consulta.where(condicion)
    return db.scalars(consulta.limit(limite).offset(desplazamiento)).all()


@router.get("/{reporte_id}", response_model=ReporteDetalle, summary="Detalle de un reporte")
def obtener(reporte_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_actual)):
    return construir_detalle(db, obtener_reporte(db, reporte_id, usuario), usuario)


@router.get("/{reporte_id}/historial", response_model=list[HistorialSalida],
            summary="Historial de cambios de estado")
def historial(reporte_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_actual)):
    return obtener_reporte(db, reporte_id, usuario).historial


@router.get("/{reporte_id}/posibles-duplicados", response_model=list[ReporteResumen],
            summary="Reportes abiertos del mismo espacio y tipo de falla (apoyo a la evaluación)")
def posibles_duplicados(reporte_id: int, db: Session = Depends(get_db), _=Depends(solo_coordinacion)):
    reporte = db.get(Reporte, reporte_id)
    if not reporte:
        raise no_encontrado("Reporte")
    return db.scalars(select(Reporte).where(
        Reporte.id != reporte.id, Reporte.espacio_id == reporte.espacio_id,
        Reporte.tipo_falla == reporte.tipo_falla, Reporte.duplicado_de_id.is_(None),
        Reporte.estado.not_in((E.RECHAZADO, E.DUPLICADO, E.CERRADO))).order_by(Reporte.id)).all()


# ------------------------------------------------------------ Fotografías
@router.post("/{reporte_id}/fotos", response_model=FotoSalida, status_code=201,
             summary="Adjuntar una fotografía (JPG, PNG o WEBP) al reporte")
def subir_foto(reporte_id: int, archivo: UploadFile = File(...), db: Session = Depends(get_db),
               usuario: Usuario = Depends(solo_reportante)):
    reporte = obtener_reporte(db, reporte_id, usuario)
    if reporte.estado in (E.CERRADO, E.RECHAZADO, E.DUPLICADO):
        raise conflicto("No se pueden adjuntar fotos a un reporte finalizado")
    if len(reporte.fotos) >= MAX_FOTOS:
        raise regla_negocio(f"Máximo {MAX_FOTOS} fotografías por reporte")
    if archivo.content_type not in FIRMAS_IMAGEN:
        raise regla_negocio("Formato no permitido: use JPG, PNG o WEBP")
    limite = configuracion.foto_max_mb * 1024 * 1024
    contenido = archivo.file.read(limite + 1)
    if len(contenido) > limite:
        raise regla_negocio(f"La fotografía supera el máximo de {configuracion.foto_max_mb} MB")
    if not contenido.startswith(FIRMAS_IMAGEN[archivo.content_type]):
        raise regla_negocio("El contenido del archivo no corresponde a una imagen válida")
    nombre = f"{uuid.uuid4().hex}{EXTENSIONES[archivo.content_type]}"
    (ruta_subidas() / nombre).write_bytes(contenido)
    foto = Foto(reporte_id=reporte.id, nombre_archivo=nombre,
                nombre_original=(archivo.filename or "foto")[:200],
                tipo_contenido=archivo.content_type, tamano_bytes=len(contenido))
    db.add(foto)
    db.commit()
    return foto


@router.get("/{reporte_id}/fotos/{foto_id}", summary="Descargar una fotografía del reporte")
def descargar_foto(reporte_id: int, foto_id: int, db: Session = Depends(get_db),
                   usuario: Usuario = Depends(usuario_actual)):
    reporte = obtener_reporte(db, reporte_id, usuario)
    foto = next((f for f in reporte.fotos if f.id == foto_id), None)
    ruta = ruta_subidas() / foto.nombre_archivo if foto else None
    if not foto or not ruta.exists():
        raise no_encontrado("Fotografía")
    return FileResponse(ruta, media_type=foto.tipo_contenido, filename=foto.nombre_original)


# ------------------------------------------------------------ Evaluación
@router.post("/{reporte_id}/valoraciones", response_model=ValoracionSalida, status_code=201,
             summary="Coordinación solicita apoyo técnico a un técnico de mantenimiento")
def solicitar_valoracion(reporte_id: int, datos: ValoracionCrear, db: Session = Depends(get_db),
                         coord: Usuario = Depends(solo_coordinacion)):
    reporte = db.get(Reporte, reporte_id)
    if not reporte:
        raise no_encontrado("Reporte")
    exigir_estado(reporte, E.REPORTADO, accion="solicitar valoración técnica de")
    tecnico = db.get(Usuario, datos.tecnico_id)
    if not tecnico or tecnico.rol != Rol.MANTENIMIENTO or not tecnico.activo:
        raise regla_negocio("El usuario indicado no es un técnico de mantenimiento activo")
    valoracion = ValoracionTecnica(reporte_id=reporte.id, tecnico_id=tecnico.id,
                                   solicitada_por_id=coord.id, indicaciones=datos.indicaciones)
    db.add(valoracion)
    db.commit()
    return valoracion


@router.post("/{reporte_id}/valoraciones/{valoracion_id}/respuesta", response_model=ValoracionSalida,
             summary="El técnico entrega su concepto técnico")
def responder_valoracion(reporte_id: int, valoracion_id: int, datos: ValoracionResponder,
                         db: Session = Depends(get_db), tecnico: Usuario = Depends(solo_mantenimiento)):
    reporte = db.get(Reporte, reporte_id)
    valoracion = next((v for v in reporte.valoraciones if v.id == valoracion_id), None) if reporte else None
    if not valoracion:
        raise no_encontrado("Solicitud de valoración")
    if valoracion.tecnico_id != tecnico.id:
        raise prohibido("Esta solicitud de valoración fue dirigida a otro técnico")
    if valoracion.fecha_respuesta:
        raise conflicto("La valoración ya fue respondida")
    valoracion.concepto = datos.concepto
    valoracion.fecha_respuesta = ahora()
    db.commit()
    return valoracion


@router.post("/{reporte_id}/evaluacion", response_model=ReporteDetalle,
             summary="Coordinación evalúa: aceptar (con prioridad), rechazar (con motivo) o marcar duplicado")
def evaluar(reporte_id: int, datos: EvaluacionEntrada, db: Session = Depends(get_db),
            coord: Usuario = Depends(solo_coordinacion)):
    reporte = db.get(Reporte, reporte_id)
    if not reporte:
        raise no_encontrado("Reporte")
    exigir_estado(reporte, E.REPORTADO, accion="evaluar")

    if datos.decision == DecisionEvaluacion.ACEPTAR:
        reporte.prioridad = datos.prioridad
        reporte.requiere_verificacion = (datos.requiere_verificacion if datos.requiere_verificacion is not None
                                         else datos.prioridad in (Prioridad.ALTA, Prioridad.CRITICA))
        nuevo, comentario = E.EVALUADO, datos.motivo or f"Aceptado con prioridad {datos.prioridad.value}"
    elif datos.decision == DecisionEvaluacion.RECHAZAR:
        reporte.motivo_rechazo = datos.motivo
        nuevo, comentario = E.RECHAZADO, datos.motivo
    else:
        original = db.get(Reporte, datos.duplicado_de_id)
        if not original or original.id == reporte.id:
            raise regla_negocio("El reporte original indicado no existe o es el mismo reporte")
        if original.estado in (E.DUPLICADO, E.RECHAZADO) or original.duplicado_de_id:
            raise regla_negocio("El reporte original no puede ser un duplicado ni estar rechazado")
        reporte.duplicado_de_id = original.id
        nuevo, comentario = E.DUPLICADO, datos.motivo or f"Duplicado del reporte #{original.id}"

    reporte.evaluado_por_id = coord.id
    reporte.fecha_evaluacion = ahora()
    cambiar_estado(db, reporte, nuevo, coord, comentario)
    db.commit()
    return construir_detalle(db, reporte, coord)


# ------------------------------------------------------------ Asignación
@router.post("/{reporte_id}/asignaciones", response_model=AsignacionSalida, status_code=201,
             summary="Asignar (o reasignar) responsable o personal de apoyo")
def asignar(reporte_id: int, datos: AsignacionCrear, db: Session = Depends(get_db),
            coord: Usuario = Depends(solo_coordinacion)):
    reporte = db.get(Reporte, reporte_id)
    if not reporte:
        raise no_encontrado("Reporte")
    exigir_estado(reporte, E.EVALUADO, E.ASIGNADO, E.EN_ATENCION, accion="asignar responsables a")
    tecnico = db.get(Usuario, datos.tecnico_id)
    if not tecnico or tecnico.rol != Rol.MANTENIMIENTO or not tecnico.activo:
        raise regla_negocio("El usuario indicado no es un técnico de mantenimiento activo")
    if not tecnico.disponible:
        raise conflicto("El técnico no está disponible actualmente")
    if es_tecnico_asignado(reporte, tecnico):
        raise conflicto("El técnico ya está asignado a este reporte")

    actual = responsable_activo(reporte)
    if datos.rol == RolAsignacion.APOYO and not actual:
        raise regla_negocio("Primero debe asignar un responsable antes de agregar personal de apoyo")
    if datos.rol == RolAsignacion.RESPONSABLE and actual:
        if not datos.motivo:
            raise regla_negocio("Para cambiar el responsable debe indicar el motivo de la reasignación")
        actual.activa = False
        actual.fecha_retiro = ahora()
        actual.motivo_retiro = f"Reasignado: {datos.motivo}"

    asignacion = Asignacion(reporte_id=reporte.id, tecnico_id=tecnico.id, asignado_por_id=coord.id,
                            rol=datos.rol, motivo=datos.motivo)
    db.add(asignacion)
    if reporte.estado == E.EVALUADO:
        cambiar_estado(db, reporte, E.ASIGNADO, coord, f"Asignado a {tecnico.nombre}")
    db.commit()
    return asignacion


@router.post("/{reporte_id}/asignaciones/{asignacion_id}/retiro", response_model=AsignacionSalida,
             summary="Retirar a una persona de apoyo (para cambiar el responsable use una nueva asignación)")
def retirar_asignacion(reporte_id: int, asignacion_id: int, datos: AsignacionRetirar,
                       db: Session = Depends(get_db), _=Depends(solo_coordinacion)):
    reporte = db.get(Reporte, reporte_id)
    asignacion = next((a for a in reporte.asignaciones if a.id == asignacion_id), None) if reporte else None
    if not asignacion:
        raise no_encontrado("Asignación")
    if not asignacion.activa:
        raise conflicto("La asignación ya fue retirada")
    if asignacion.rol == RolAsignacion.RESPONSABLE:
        raise conflicto("No se puede retirar al responsable; asigne uno nuevo para reemplazarlo")
    asignacion.activa = False
    asignacion.fecha_retiro = ahora()
    asignacion.motivo_retiro = datos.motivo
    db.commit()
    return asignacion


# ------------------------------------------------------------ Intervenciones
@router.post("/{reporte_id}/intervenciones", response_model=IntervencionSalida, status_code=201,
             summary="El técnico asignado registra su intervención")
def registrar_intervencion(reporte_id: int, datos: IntervencionCrear, db: Session = Depends(get_db),
                           tecnico: Usuario = Depends(solo_mantenimiento)):
    reporte = obtener_reporte(db, reporte_id, tecnico)
    if not es_tecnico_asignado(reporte, tecnico):
        raise prohibido("Solo el personal asignado al reporte puede registrar intervenciones")
    exigir_estado(reporte, E.ASIGNADO, E.EN_ATENCION, accion="registrar intervenciones en")
    if datos.fecha_intervencion < reporte.fecha_inicio_falla:
        raise regla_negocio("La fecha de la intervención no puede ser anterior al inicio de la falla")
    intervencion = Intervencion(reporte_id=reporte.id, tecnico_id=tecnico.id, **datos.model_dump())
    db.add(intervencion)
    if reporte.estado == E.ASIGNADO:
        cambiar_estado(db, reporte, E.EN_ATENCION, tecnico, "Primera intervención registrada")
    db.commit()
    return intervencion


@router.get("/{reporte_id}/intervenciones", response_model=list[IntervencionSalida],
            summary="Historial de intervenciones del reporte")
def listar_intervenciones(reporte_id: int, db: Session = Depends(get_db),
                          usuario: Usuario = Depends(usuario_actual)):
    return obtener_reporte(db, reporte_id, usuario).intervenciones


# ------------------------------------------------------------ Cierre
@router.post("/{reporte_id}/finalizar", response_model=ReporteDetalle,
             summary="El responsable informa que terminó (o coordinación cierra directamente)")
def finalizar(reporte_id: int, datos: FinalizarEntrada, db: Session = Depends(get_db),
              usuario: Usuario = Depends(requiere_roles(Rol.MANTENIMIENTO, Rol.COORDINACION))):
    reporte = obtener_reporte(db, reporte_id, usuario)
    if usuario.rol == Rol.MANTENIMIENTO:
        responsable = responsable_activo(reporte)
        if not responsable or responsable.tecnico_id != usuario.id:
            raise prohibido("Solo el responsable asignado puede finalizar el reporte")
    exigir_estado(reporte, E.EN_ATENCION, accion="finalizar")
    if not reporte.intervenciones:
        raise conflicto("No se puede cerrar un reporte sin al menos una intervención registrada")

    reporte.resultado_cierre = datos.resultado
    reporte.descripcion_solucion = datos.descripcion_solucion
    reporte.motivo_cierre = datos.motivo
    reporte.finalizado_por_id = usuario.id
    necesita_verificacion = (usuario.rol == Rol.MANTENIMIENTO and
                             (reporte.requiere_verificacion or datos.resultado != ResultadoCierre.RESUELTO))
    if necesita_verificacion:
        cambiar_estado(db, reporte, E.EN_VERIFICACION, usuario,
                       f"Trabajo finalizado ({datos.resultado.value}); pendiente de verificación")
    else:
        reporte.fecha_cierre = ahora()
        if usuario.rol == Rol.COORDINACION:
            reporte.verificado_por_id = usuario.id
        cambiar_estado(db, reporte, E.CERRADO, usuario, f"Cerrado: {datos.resultado.value}")
    db.commit()
    return construir_detalle(db, reporte, usuario)


@router.post("/{reporte_id}/verificacion", response_model=ReporteDetalle,
             summary="Coordinación verifica el trabajo: aprueba el cierre o lo devuelve a atención")
def verificar(reporte_id: int, datos: VerificarEntrada, db: Session = Depends(get_db),
              coord: Usuario = Depends(solo_coordinacion)):
    reporte = db.get(Reporte, reporte_id)
    if not reporte:
        raise no_encontrado("Reporte")
    exigir_estado(reporte, E.EN_VERIFICACION, accion="verificar")
    if datos.aprobado:
        reporte.verificado_por_id = coord.id
        reporte.fecha_cierre = ahora()
        cambiar_estado(db, reporte, E.CERRADO, coord, datos.comentario or "Cierre verificado")
    else:
        reporte.resultado_cierre = reporte.descripcion_solucion = reporte.motivo_cierre = None
        reporte.finalizado_por_id = None
        cambiar_estado(db, reporte, E.EN_ATENCION, coord, f"Verificación no aprobada: {datos.comentario}")
    db.commit()
    return construir_detalle(db, reporte, coord)
