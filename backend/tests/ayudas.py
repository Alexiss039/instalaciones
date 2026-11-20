"""Funciones auxiliares para armar escenarios en las pruebas (todas usan la API)."""
from datetime import timedelta

import pytest
from app.config import hoy_local

prueba = pytest.mark.prueba


def dias(n: int = 0) -> str:
    """Fecha en la zona de la organización, desplazada n días (negativa = pasado)."""
    return (hoy_local() + timedelta(days=n)).isoformat()


HOY = dias()
AYER = dias(-1)


def crear_reporte(c, datos, quien="doc", espacio=None, **extra):
    cuerpo = {"espacio_id": espacio or datos.aula, "descripcion": "La lámpara del salón no enciende",
              "fecha_inicio_falla": AYER, "tipo_falla": "iluminacion", **extra}
    r = c.post("/reportes", json=cuerpo, headers=getattr(datos.h, quien))
    assert r.status_code == 201, r.text
    return r.json()["id"]


def evaluar_aceptar(c, datos, rid, prioridad="media", **extra):
    r = c.post(f"/reportes/{rid}/evaluacion", headers=datos.h.coord,
               json={"decision": "aceptar", "prioridad": prioridad, **extra})
    assert r.status_code == 200, r.text
    return r.json()


def asignar(c, datos, rid, tecnico="tec1", **extra):
    r = c.post(f"/reportes/{rid}/asignaciones", headers=datos.h.coord,
               json={"tecnico_id": datos.ids[tecnico], **extra})
    assert r.status_code == 201, r.text
    return r.json()


def intervenir(c, datos, rid, tecnico="tec1", **extra):
    cuerpo = {"fecha_intervencion": HOY, "actividades": "Cambio de la lámpara y revisión del circuito",
              "tiempo_minutos": 45, "resultado": "Iluminación restablecida", **extra}
    r = c.post(f"/reportes/{rid}/intervenciones", json=cuerpo, headers=getattr(datos.h, tecnico))
    assert r.status_code == 201, r.text
    return r.json()


def reporte_en_atencion(c, datos, prioridad="media", **extra):
    rid = crear_reporte(c, datos, **extra)
    evaluar_aceptar(c, datos, rid, prioridad)
    asignar(c, datos, rid)
    intervenir(c, datos, rid)
    return rid


FINALIZAR = {"resultado": "resuelto", "descripcion_solucion": "Se reemplazó la lámpara defectuosa"}
