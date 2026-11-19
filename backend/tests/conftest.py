"""Configuración de pruebas: BD en memoria por prueba, usuarios de ejemplo y registro de evidencias.

Para generar los archivos de evidencia en ../evidencias/:  EVIDENCIAS=1 pytest
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import database, seguridad  # noqa: E402
from app.dependencias import get_db  # noqa: E402
from app.enums import Cargo, Rol, TipoEspacio, TipoFalla  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Edificio, Espacio, Usuario  # noqa: E402

seguridad.ITERACIONES = 1000  # contraseñas rápidas de hashear solo durante las pruebas
RAIZ = Path(__file__).resolve().parents[2]
PASSWORD = "Prueba1234"

BASE = ("BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil "
        "(coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada.")

# Condiciones iniciales y resultado esperado de cada prueba (se muestran en las evidencias).
CONTEXTO = {
    "PF-01": ("BASE", "HTTP 201 con estado «reportado»; el reporte se puede consultar después con los mismos datos."),
    "PF-02": ("BASE", "HTTP 422 con el detalle de cada campo inválido; no se crea ningún reporte."),
    "PF-03": ('BASE + 3 reportes creados por el docente.', 'Coordinación recibe HTTP 200 con los 3 reportes del más reciente al más antiguo; el detalle trae edificio, espacio y teléfono del reportante.'),
    "PF-04": ("BASE", "HTTP 404 con mensaje y código de error controlados, sin excepción del servidor."),
    "PF-05": ("BASE + reportes en estado «reportado».", "Aceptar: estado «evaluado» con prioridad. Rechazar con motivo: estado «rechazado». Ambas decisiones quedan en el historial."),
    "PF-06": ('BASE + reporte recién creado (estado «reportado»).', 'Asignar o finalizar antes de evaluar da HTTP 409; rechazar un reporte ya evaluado da HTTP 409 y el estado se mantiene «evaluado».'),
    "PF-07": ("BASE + reporte evaluado.", "HTTP 201; el reporte pasa a «asignado» y el técnico responsable lo ve en su lista."),
    "PF-08": ('BASE + reporte en estado «reportado».', 'HTTP 401 sin sesión y HTTP 403 para docente o técnico en evaluación, asignación, dashboard y usuarios; el reporte queda sin prioridad ni asignaciones.'),
    "PF-09": ("BASE + reporte asignado al técnico.", "HTTP 201; la intervención queda vinculada al reporte y el estado pasa a «en atención»."),
    "PF-10": ("BASE + reporte en atención con una intervención registrada.", "Estado «cerrado» con resultado y descripción de la solución; el historial muestra todas las transiciones."),
    "PF-11": ("BASE + reportes en distintos estados, prioridades y tipos.", "Los conteos del dashboard coinciden con los reportes creados y los filtros reducen el resultado de forma coherente."),
    "PF-12": ("BASE", "Todo el recorrido responde sin error y el reporte termina «cerrado» con su historial completo."),
    "PF-13": ("BASE + reporte original y reportes del mismo problema.", "Los duplicados quedan vinculados al original y todos los reportantes se conservan."),
    "PF-14": ('BASE', 'Registro HTTP 201 (rol reportante, sin devolver la contraseña); correo repetido 409; contraseña débil 422; login incorrecto 401; login correcto 200; token falso 401.'),
    "PF-15": ("BASE + reporte «en verificación».", "Si coordinación rechaza el cierre, el reporte vuelve a «en atención»."),
    "PF-16": ("BASE + reporte asignado.", "Reasignar sin motivo HTTP 422; con motivo se conserva el historial; un técnico no disponible se rechaza."),
    "PF-17": ('BASE + un reporte del docente y otro del administrativo.', 'El docente ve solo el suyo (200) y recibe 403 al abrir el ajeno o su historial; coordinación ve ambos.'),
    "PF-18": ('BASE + reporte del docente.', 'JPG válido HTTP 201; ejecutable y falso PNG HTTP 422; otro reportante HTTP 403; el reporte conserva 1 foto.'),
    "PF-19": ('BASE', 'Un reportante lista espacios (200) pero crear da 403; coordinación crea (201) y un nombre repetido en el mismo edificio da 409.'),
}

_registro: dict[str, dict] = {}   # id de prueba -> datos de la evidencia
_actual: dict = {}


def pytest_configure(config):
    config.addinivalue_line("markers", "prueba(id, titulo, requisito, ca): metadatos de la prueba funcional")


class ClienteRegistrado(TestClient):
    """TestClient que anota cada petición y respuesta para generar las evidencias."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.quien: dict[str, str] = {}   # token -> etiqueta (rol) para las evidencias

    def request(self, method, url, *, silencioso=False, **kwargs):
        respuesta = super().request(method, url, **kwargs)
        if not silencioso and _actual:
            cuerpo = kwargs.get("json") or kwargs.get("data")
            if isinstance(cuerpo, dict):
                cuerpo = {k: ("***" if "password" in k else v) for k, v in cuerpo.items()}
            elif kwargs.get("files"):
                cuerpo = "(archivo adjunto)"
            token = (kwargs.get("headers") or {}).get("Authorization", "")[7:]
            try:
                salida = respuesta.json()
            except ValueError:
                salida = f"({respuesta.headers.get('content-type')}, {len(respuesta.content)} bytes)"
            _actual["pasos"].append({
                "metodo": method.upper(), "ruta": str(url), "params": kwargs.get("params"),
                "usuario": self.quien.get(token, "sin sesión"), "cuerpo": cuerpo,
                "estado": respuesta.status_code, "respuesta": salida})
        return respuesta


@pytest.fixture()
def cliente():
    motor = database.crear_motor("sqlite://", poolclass=StaticPool)
    database.crear_tablas(motor)
    SesionPrueba = database.sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)

    def _get_db():
        with SesionPrueba() as db:
            yield db

    app.dependency_overrides[get_db] = _get_db
    c = ClienteRegistrado(app)
    c.SesionPrueba = SesionPrueba
    yield c
    app.dependency_overrides.clear()
    motor.dispose()


@pytest.fixture()
def datos(cliente, tmp_path, monkeypatch):
    """Edificios, espacios y una cuenta por perfil, con sus cabeceras de autenticación."""
    from app import config
    monkeypatch.setattr(config.configuracion, "carpeta_subidas", str(tmp_path / "subidas"))

    with cliente.SesionPrueba() as db:
        bloque = Edificio(nombre="Bloque A")
        db.add(bloque)
        db.flush()
        espacios = [Espacio(edificio_id=bloque.id, nombre="Aula 101", tipo=TipoEspacio.AULA),
                    Espacio(edificio_id=bloque.id, nombre="Laboratorio 1", tipo=TipoEspacio.LABORATORIO),
                    Espacio(edificio_id=bloque.id, nombre="Cafetería", tipo=TipoEspacio.ZONA_COMUN)]
        cuentas = {
            "coord": ("Coordinación Prueba", Rol.COORDINACION, None, [], 0),
            "tec1": ("Técnico Uno", Rol.MANTENIMIENTO, None, [TipoFalla.ELECTRICA.value], 6),
            "tec2": ("Técnico Dos", Rol.MANTENIMIENTO, None, [TipoFalla.PLOMERIA.value], 2),
            "doc": ("Docente Prueba", Rol.REPORTANTE, Cargo.DOCENTE, [], 0),
            "adm": ("Administrativo Prueba", Rol.REPORTANTE, Cargo.ADMINISTRATIVO, [], 0),
        }
        usuarios = {}
        for clave, (nombre, rol, cargo, esp, exp) in cuentas.items():
            u = Usuario(nombre=nombre, correo=f"{clave}@prueba.test", telefono="3001112233",
                        password_hash=seguridad.hashear_password(PASSWORD), rol=rol, cargo=cargo,
                        especialidades=esp, experiencia_anios=exp)
            db.add(u)
            usuarios[clave] = u
        db.add_all(espacios)
        db.commit()
        ids = {k: u.id for k, u in usuarios.items()}
        espacio_ids = [e.id for e in espacios]

    cabeceras = {}
    for clave in cuentas:
        r = cliente.request("POST", "/auth/login", silencioso=True,
                            data={"username": f"{clave}@prueba.test", "password": PASSWORD})
        token = r.json()["access_token"]
        cabeceras[clave] = {"Authorization": f"Bearer {token}"}
        cliente.quien[token] = {"coord": "coordinación", "tec1": "mantenimiento (Técnico Uno)",
                                "tec2": "mantenimiento (Técnico Dos)", "doc": "reportante (docente)",
                                "adm": "reportante (administrativo)"}[clave]
    return SimpleNamespace(ids=ids, h=SimpleNamespace(**cabeceras), aula=espacio_ids[0],
                           lab=espacio_ids[1], cafeteria=espacio_ids[2])


# ----------------------------------------------------------------- Evidencias
@pytest.fixture(autouse=True)
def _marca_de_prueba(request):
    global _actual
    marca = request.node.get_closest_marker("prueba")
    _actual = {}
    if marca:
        previo, esperado = CONTEXTO.get(marca.args[0], ("", ""))
        _actual = {"id": marca.args[0], "titulo": marca.args[1], **marca.kwargs, "pasos": [],
                   "previo": BASE if previo == "BASE" else previo.replace("BASE", BASE.rstrip("."), 1),
                   "esperado": esperado,
                   "nodo": request.node.name}
        _registro[_actual["id"]] = _actual
    yield
    _actual = {}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    resultado = yield
    informe = resultado.get_result()
    marca = item.get_closest_marker("prueba")
    if marca and informe.when == "call":
        _registro[marca.args[0]]["resultado"] = "APROBADA" if informe.passed else "FALLIDA"
        if informe.failed:
            _registro[marca.args[0]]["error"] = str(informe.longrepr)[-1500:]


def pytest_sessionfinish(session, exitstatus):
    if os.environ.get("EVIDENCIAS") != "1" or not _registro:
        return
    carpeta = RAIZ / "evidencias"
    carpeta.mkdir(exist_ok=True)
    pruebas = sorted(_registro.values(), key=lambda p: p["id"])
    (carpeta / "resultados_pruebas.json").write_text(
        json.dumps(pruebas, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    lineas = ["# Evidencias de las pruebas funcionales de la API", "",
              f"Generado automáticamente con `EVIDENCIAS=1 pytest` el {datetime.now():%Y-%m-%d %H:%M}.", "",
              "| ID | Prueba | Requisito | CA | Resultado |", "|---|---|---|---|---|"]
    for p in pruebas:
        lineas.append(f"| {p['id']} | {p['titulo']} | {p.get('requisito', '')} | {p.get('ca', '')} | "
                      f"{p.get('resultado', 'NO EJECUTADA')} |")
    for p in pruebas:
        lineas += ["", f"## {p['id']} - {p['titulo']}", "",
                   f"- **Requisito:** {p.get('requisito', '')}  |  **Criterio:** {p.get('ca', '')}",
                   f"- **Condiciones iniciales:** {p.get('previo', '')}",
                   f"- **Resultado esperado:** {p.get('esperado', '')}",
                   f"- **Resultado obtenido:** {p.get('resultado', 'NO EJECUTADA')}", "", "Pasos ejecutados contra la API:", ""]
        for i, paso in enumerate(p["pasos"], 1):
            lineas.append(f"{i}. `{paso['metodo']} {paso['ruta']}` como *{paso['usuario']}* "
                          f"→ **HTTP {paso['estado']}**")
            if paso["params"]:
                lineas.append(f"   - Parámetros: `{json.dumps(paso['params'], ensure_ascii=False)}`")
            if paso["cuerpo"]:
                lineas.append(f"   - Entrada: `{json.dumps(paso['cuerpo'], ensure_ascii=False, default=str)}`")
            texto = json.dumps(paso["respuesta"], ensure_ascii=False, default=str)
            lineas.append(f"   - Respuesta: `{texto[:600]}{'…' if len(texto) > 600 else ''}`")
        if p.get("error"):
            lineas += ["", "```", p["error"], "```"]
    (carpeta / "pruebas_api.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
