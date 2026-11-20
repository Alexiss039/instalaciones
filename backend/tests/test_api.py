"""Pruebas funcionales de la API. PF-01 a PF-12 son las mínimas de la guía; PF-13 en adelante, adicionales."""
import io

from ayudas import (AYER, FINALIZAR, HOY, asignar, crear_reporte, dias, evaluar_aceptar, intervenir,
                    prueba, reporte_en_atencion)


@prueba("PF-01", "Registrar un reporte válido vinculado a un espacio y comprobar que persiste",
        requisito="RF-03, RF-05", ca="CA-01")
def test_pf01_crear_reporte_valido(cliente, datos):
    r = cliente.post("/reportes", headers=datos.h.doc, json={
        "espacio_id": datos.aula, "descripcion": "El proyector del aula no enciende",
        "fecha_inicio_falla": AYER, "tipo_falla": "electrica", "urgencia_reportada": "alta"})
    assert r.status_code == 201
    creado = r.json()
    assert creado["estado"] == "reportado" and creado["grupo"] == "pendiente"
    assert creado["espacio"]["nombre"] == "Aula 101" and creado["creador"]["nombre"] == "Docente Prueba"
    consulta = cliente.get(f"/reportes/{creado['id']}", headers=datos.h.doc)
    assert consulta.status_code == 200
    assert consulta.json()["descripcion"] == "El proyector del aula no enciende"
    assert consulta.json()["historial"][0]["estado_nuevo"] == "reportado"


@prueba("PF-02", "Rechazar reportes con datos obligatorios faltantes o inválidos sin crear registros",
        requisito="RF-03, RNF-02", ca="CA-01")
def test_pf02_reporte_invalido(cliente, datos):
    base = {"espacio_id": datos.aula, "descripcion": "Descripción suficiente", "fecha_inicio_falla": AYER}
    casos = [
        {k: v for k, v in base.items() if k != "descripcion"},                       # falta descripción
        {**base, "descripcion": "corta"},                                           # descripción muy corta
        {**base, "fecha_inicio_falla": dias(3)},  # fecha futura
        {**base, "fecha_inicio_falla": "no-es-fecha"},                              # fecha malformada
        {**base, "tipo_falla": "inventada"},                                        # valor fuera del catálogo
        {**base, "espacio_id": 99999},                                              # espacio inexistente
    ]
    for cuerpo in casos:
        r = cliente.post("/reportes", headers=datos.h.doc, json=cuerpo)
        assert r.status_code == 422, cuerpo
        assert "detalle" in r.json()
    assert cliente.get("/reportes", headers=datos.h.coord).json() == []


@prueba("PF-03", "Consultar el listado de reportes y el detalle de un reporte",
        requisito="RF-05", ca="CA-01")
def test_pf03_listar_y_detallar(cliente, datos):
    ids = [crear_reporte(cliente, datos, descripcion=f"Falla número {i} en el aula") for i in range(3)]
    lista = cliente.get("/reportes", headers=datos.h.coord)
    assert lista.status_code == 200 and [x["id"] for x in lista.json()] == sorted(ids, reverse=True)
    detalle = cliente.get(f"/reportes/{ids[0]}", headers=datos.h.coord)
    assert detalle.status_code == 200
    assert detalle.json()["espacio"]["edificio"]["nombre"] == "Bloque A"
    assert detalle.json()["reportantes"][0]["usuario"]["telefono"] == "3001112233"


@prueba("PF-04", "Consultar un reporte inexistente y recibir un error HTTP controlado",
        requisito="RNF-02", ca="CA-01")
def test_pf04_reporte_inexistente(cliente, datos):
    r = cliente.get("/reportes/99999", headers=datos.h.coord)
    assert r.status_code == 404
    assert r.json() == {"detalle": "Reporte no encontrado", "codigo": 404}


@prueba("PF-05", "Evaluar un reporte (aceptar con prioridad / rechazar con motivo) y registrar la decisión",
        requisito="RF-06", ca="CA-02")
def test_pf05_evaluar_reporte(cliente, datos):
    a = crear_reporte(cliente, datos)
    b = crear_reporte(cliente, datos, descripcion="Solicito pintar toda la fachada del edificio")
    aceptado = evaluar_aceptar(cliente, datos, a, "alta")
    assert aceptado["estado"] == "evaluado" and aceptado["prioridad"] == "alta"
    assert aceptado["requiere_verificacion"] is True    # prioridad alta exige verificación
    sin_motivo = cliente.post(f"/reportes/{b}/evaluacion", headers=datos.h.coord, json={"decision": "rechazar"})
    assert sin_motivo.status_code == 422
    rechazado = cliente.post(f"/reportes/{b}/evaluacion", headers=datos.h.coord,
                             json={"decision": "rechazar", "motivo": "No corresponde a las instalaciones"})
    assert rechazado.status_code == 200
    assert rechazado.json()["estado"] == "rechazado"
    assert rechazado.json()["motivo_rechazo"] == "No corresponde a las instalaciones"
    sin_prioridad = cliente.post(f"/reportes/{crear_reporte(cliente, datos)}/evaluacion",
                                 headers=datos.h.coord, json={"decision": "aceptar"})
    assert sin_prioridad.status_code == 422


@prueba("PF-06", "Rechazar transiciones de estado no permitidas", requisito="RF-08", ca="CA-02")
def test_pf06_transicion_no_permitida(cliente, datos):
    rid = crear_reporte(cliente, datos)
    # Asignar o cerrar un reporte que aún no fue evaluado
    r1 = cliente.post(f"/reportes/{rid}/asignaciones", headers=datos.h.coord, json={"tecnico_id": datos.ids["tec1"]})
    r2 = cliente.post(f"/reportes/{rid}/finalizar", headers=datos.h.coord, json=FINALIZAR)
    assert (r1.status_code, r2.status_code) == (409, 409)
    evaluar_aceptar(cliente, datos, rid)
    r3 = cliente.post(f"/reportes/{rid}/evaluacion", headers=datos.h.coord,
                      json={"decision": "rechazar", "motivo": "Intento de rechazo tardío"})
    assert r3.status_code == 409
    assert cliente.get(f"/reportes/{rid}", headers=datos.h.coord).json()["estado"] == "evaluado"


@prueba("PF-07", "Asignar un responsable autorizado y comprobar su persistencia y visibilidad",
        requisito="RF-09, RF-05", ca="CA-03")
def test_pf07_asignar_responsable(cliente, datos):
    rid = crear_reporte(cliente, datos)
    evaluar_aceptar(cliente, datos, rid)
    r = cliente.post(f"/reportes/{rid}/asignaciones", headers=datos.h.coord,
                     json={"tecnico_id": datos.ids["tec1"]})
    assert r.status_code == 201 and r.json()["rol"] == "responsable"
    detalle = cliente.get(f"/reportes/{rid}", headers=datos.h.coord).json()
    assert detalle["estado"] == "asignado" and detalle["asignaciones"][0]["tecnico"]["nombre"] == "Técnico Uno"
    assert [x["id"] for x in cliente.get("/reportes", headers=datos.h.tec1).json()] == [rid]
    assert cliente.get("/reportes", headers=datos.h.tec2).json() == []
    # el técnico asignado también ve el criterio de elección en el listado de técnicos
    tecnicos = cliente.get("/tecnicos", headers=datos.h.coord, params={"tipo_falla": "iluminacion"}).json()
    assert {t["nombre"]: t["trabajos_pendientes"] for t in tecnicos}["Técnico Uno"] == 1


@prueba("PF-08", "Bloquear gestiones de usuarios no autorizados sin modificar datos",
        requisito="RNF-01", ca="CA-02, CA-03")
def test_pf08_usuario_no_autorizado(cliente, datos):
    rid = crear_reporte(cliente, datos)
    evaluacion = {"decision": "aceptar", "prioridad": "alta"}
    assert cliente.post(f"/reportes/{rid}/evaluacion", headers=datos.h.doc, json=evaluacion).status_code == 403
    assert cliente.post(f"/reportes/{rid}/evaluacion", headers=datos.h.tec1, json=evaluacion).status_code == 403
    assert cliente.post(f"/reportes/{rid}/evaluacion", json=evaluacion).status_code == 401
    asignacion = {"tecnico_id": datos.ids["tec1"]}
    assert cliente.post(f"/reportes/{rid}/asignaciones", headers=datos.h.tec1, json=asignacion).status_code == 403
    assert cliente.get("/dashboard/resumen", headers=datos.h.doc).status_code == 403
    assert cliente.get("/usuarios", headers=datos.h.tec1).status_code == 403
    detalle = cliente.get(f"/reportes/{rid}", headers=datos.h.coord).json()
    assert detalle["estado"] == "reportado" and detalle["prioridad"] is None and detalle["asignaciones"] == []


@prueba("PF-09", "Registrar una intervención válida vinculada al reporte", requisito="RF-10", ca="CA-04")
def test_pf09_registrar_intervencion(cliente, datos):
    rid = crear_reporte(cliente, datos)
    evaluar_aceptar(cliente, datos, rid)
    asignar(cliente, datos, rid)
    r = cliente.post(f"/reportes/{rid}/intervenciones", headers=datos.h.tec1, json={
        "fecha_intervencion": HOY, "actividades": "Diagnóstico del circuito de iluminación",
        "tiempo_minutos": 30, "resultado": "Se identificó el balastro dañado"})
    assert r.status_code == 201 and r.json()["tecnico"]["nombre"] == "Técnico Uno"
    detalle = cliente.get(f"/reportes/{rid}", headers=datos.h.coord).json()
    assert detalle["estado"] == "en_atencion" and len(detalle["intervenciones"]) == 1
    # casos inválidos: técnico no asignado, tiempo inválido y fecha anterior a la falla
    cuerpo = {"fecha_intervencion": HOY, "actividades": "Actividad de prueba", "tiempo_minutos": 10, "resultado": "Sin novedad"}
    assert cliente.post(f"/reportes/{rid}/intervenciones", headers=datos.h.tec2, json=cuerpo).status_code == 403
    assert cliente.post(f"/reportes/{rid}/intervenciones", headers=datos.h.tec1,
                        json={**cuerpo, "tiempo_minutos": 0}).status_code == 422
    assert cliente.post(f"/reportes/{rid}/intervenciones", headers=datos.h.tec1,
                        json={**cuerpo, "fecha_intervencion": "2000-01-01"}).status_code == 422
    assert len(cliente.get(f"/reportes/{rid}/intervenciones", headers=datos.h.tec1).json()) == 1


@prueba("PF-10", "Cerrar un reporte y consultar el resultado del cierre con su historial",
        requisito="RF-11, RF-08", ca="CA-05")
def test_pf10_cerrar_reporte(cliente, datos):
    sin_trabajo = crear_reporte(cliente, datos)
    evaluar_aceptar(cliente, datos, sin_trabajo)
    asignar(cliente, datos, sin_trabajo)
    assert cliente.post(f"/reportes/{sin_trabajo}/finalizar", headers=datos.h.tec1, json=FINALIZAR).status_code == 409

    rid = reporte_en_atencion(cliente, datos, "media")
    r = cliente.post(f"/reportes/{rid}/finalizar", headers=datos.h.tec1, json=FINALIZAR)
    assert r.status_code == 200 and r.json()["estado"] == "cerrado"
    visto_por_reportante = cliente.get(f"/reportes/{rid}", headers=datos.h.doc).json()
    assert visto_por_reportante["resultado_cierre"] == "resuelto"
    assert visto_por_reportante["descripcion_solucion"] == FINALIZAR["descripcion_solucion"]
    estados = [h["estado_nuevo"] for h in visto_por_reportante["historial"]]
    assert estados == ["reportado", "evaluado", "asignado", "en_atencion", "cerrado"]
    # un reporte cerrado no admite más cambios
    assert cliente.post(f"/reportes/{rid}/finalizar", headers=datos.h.tec1, json=FINALIZAR).status_code == 409


@prueba("PF-11", "Consultar el dashboard con conteos y filtros coherentes",
        requisito="RF-12", ca="CA-06")
def test_pf11_dashboard(cliente, datos):
    a = crear_reporte(cliente, datos, tipo_falla="electrica")
    crear_reporte(cliente, datos, "adm", espacio=datos.lab, tipo_falla="electrica")
    crear_reporte(cliente, datos, espacio=datos.aula, tipo_falla="plomeria")
    evaluar_aceptar(cliente, datos, a)
    asignar(cliente, datos, a)
    intervenir(cliente, datos, a)
    resumen = cliente.get("/dashboard/resumen", headers=datos.h.coord)
    assert resumen.status_code == 200
    r = resumen.json()
    assert r["total_reportes"] == 3
    assert {g["clave"]: g["total"] for g in r["por_grupo"]} == {"pendiente": 2, "en_atencion": 1}
    assert r["fallas_mas_frecuentes"][0] == {"clave": "electrica", "etiqueta": "electrica", "total": 2}
    assert r["espacios_afectados"][0]["etiqueta"] == "Bloque A - Aula 101" and r["espacios_afectados"][0]["total"] == 2
    assert r["por_responsable"] == [{"clave": str(datos.ids["tec1"]), "etiqueta": "Técnico Uno", "total": 1}]
    # filtros por fecha
    hoy = cliente.get("/dashboard/resumen", headers=datos.h.coord, params={"desde": HOY, "hasta": HOY}).json()
    assert hoy["total_reportes"] == 3
    futuro = dias(5)
    assert cliente.get("/dashboard/resumen", headers=datos.h.coord, params={"desde": futuro}).json()["total_reportes"] == 0
    assert cliente.get("/dashboard/resumen", headers=datos.h.coord,
                       params={"desde": futuro, "hasta": HOY}).status_code == 422
    # el listado filtrado coincide con el dashboard
    filtrado = cliente.get("/reportes", headers=datos.h.coord, params={"grupo": "pendiente", "tipo_falla": "electrica"})
    assert len(filtrado.json()) == 1


@prueba("PF-12", "Flujo completo por API: reporte, foto, valoración, evaluación, asignación, intervención, "
        "verificación y cierre", requisito="RF-03 a RF-12", ca="CA-01 a CA-06")
def test_pf12_flujo_completo(cliente, datos):
    rid = crear_reporte(cliente, datos, tipo_falla="electrica", urgencia_reportada="alta")
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 64
    foto = cliente.post(f"/reportes/{rid}/fotos", headers=datos.h.doc, files={"archivo": ("falla.png", io.BytesIO(png), "image/png")})
    assert foto.status_code == 201
    val = cliente.post(f"/reportes/{rid}/valoraciones", headers=datos.h.coord,
                       json={"tecnico_id": datos.ids["tec1"], "indicaciones": "Revisar si es falla eléctrica"})
    assert val.status_code == 201
    assert cliente.get("/reportes", headers=datos.h.tec1).json()[0]["id"] == rid   # el técnico ve lo que debe valorar
    assert cliente.post(f"/reportes/{rid}/valoraciones/{val.json()['id']}/respuesta", headers=datos.h.tec1,
                        json={"concepto": "Falla en el tablero, requiere intervención eléctrica"}).status_code == 200
    assert evaluar_aceptar(cliente, datos, rid, "alta")["requiere_verificacion"] is True
    asignar(cliente, datos, rid, "tec1")
    asignar(cliente, datos, rid, "tec2", rol="apoyo")
    intervenir(cliente, datos, rid, "tec1")
    intervenir(cliente, datos, rid, "tec2", actividades="Apoyo en el cableado del tablero")
    fin = cliente.post(f"/reportes/{rid}/finalizar", headers=datos.h.tec1, json=FINALIZAR)
    assert fin.json()["estado"] == "en_verificacion"
    ok = cliente.post(f"/reportes/{rid}/verificacion", headers=datos.h.coord, json={"aprobado": True})
    assert ok.json()["estado"] == "cerrado" and len(ok.json()["intervenciones"]) == 2
    assert {i["tecnico"]["nombre"] for i in ok.json()["intervenciones"]} == {"Técnico Uno", "Técnico Dos"}
    visto = cliente.get(f"/reportes/{rid}", headers=datos.h.doc).json()
    assert visto["estado"] == "cerrado" and len(visto["fotos"]) == 1
    descarga = cliente.get(f"/reportes/{rid}/fotos/{foto.json()['id']}", headers=datos.h.coord)
    assert descarga.status_code == 200 and descarga.content == png
    r = cliente.get("/dashboard/resumen", headers=datos.h.coord).json()
    assert r["por_grupo"] == [{"clave": "finalizado", "etiqueta": "finalizado", "total": 1}]
    assert r["por_resultado_cierre"][0]["clave"] == "resuelto"


# ---------------------------------------------------------------- Pruebas adicionales
@prueba("PF-13", "Reportes duplicados: se vinculan al original y se conservan todos los reportantes",
        requisito="RF-07", ca="CA-02")
def test_pf13_duplicados(cliente, datos):
    original = crear_reporte(cliente, datos, "doc")
    repetido = crear_reporte(cliente, datos, "adm")
    posibles = cliente.get(f"/reportes/{repetido}/posibles-duplicados", headers=datos.h.coord)
    assert [x["id"] for x in posibles.json()] == [original]
    # sin indicar el original, la solicitud es inválida
    assert cliente.post(f"/reportes/{repetido}/evaluacion", headers=datos.h.coord,
                        json={"decision": "duplicado"}).status_code == 422
    r = cliente.post(f"/reportes/{repetido}/evaluacion", headers=datos.h.coord,
                     json={"decision": "duplicado", "duplicado_de_id": original})
    assert r.status_code == 200 and r.json()["estado"] == "duplicado"
    assert cliente.post(f"/reportes/{original}/evaluacion", headers=datos.h.coord,
                        json={"decision": "duplicado", "duplicado_de_id": original}).status_code == 422
    evaluar_aceptar(cliente, datos, original)
    detalle = cliente.get(f"/reportes/{original}", headers=datos.h.coord).json()
    assert [(x["usuario"]["nombre"], x["es_reporte_original"]) for x in detalle["reportantes"]] == [
        ("Docente Prueba", True), ("Administrativo Prueba", False)]
    # quien reportó el duplicado puede seguir el avance del caso original
    suyo = cliente.get(f"/reportes/{repetido}", headers=datos.h.adm).json()
    assert suyo["estado_reporte_original"] == "evaluado" and suyo["reportantes"] == []
    # el original no cuenta dos veces en el dashboard de pendientes
    assert cliente.get("/dashboard/resumen", headers=datos.h.coord).json()["por_grupo"][0]["total"] == 1


@prueba("PF-14", "Autenticación: registro, credenciales incorrectas y correo repetido",
        requisito="RF-01, RNF-03", ca="CA-01")
def test_pf14_autenticacion(cliente, datos):
    nuevo = {"nombre": "Docente Nuevo", "correo": "NUEVO@Prueba.test", "telefono": "3112223344",
             "password": "Clave12345", "cargo": "docente"}
    r = cliente.post("/auth/registro", json=nuevo)
    assert r.status_code == 201 and r.json()["rol"] == "reportante" and "password" not in r.text
    assert cliente.post("/auth/registro", json=nuevo).status_code == 409
    assert cliente.post("/auth/registro", json={**nuevo, "correo": "otro@prueba.test", "password": "sololetras"}).status_code == 422
    malo = cliente.post("/auth/login", data={"username": "nuevo@prueba.test", "password": "incorrecta1"})
    assert malo.status_code == 401
    bueno = cliente.post("/auth/login", data={"username": "nuevo@prueba.test", "password": "Clave12345"})
    assert bueno.status_code == 200 and bueno.json()["usuario"]["correo"] == "nuevo@prueba.test"
    yo = cliente.get("/auth/yo", headers={"Authorization": f"Bearer {bueno.json()['access_token']}"})
    assert yo.status_code == 200
    assert cliente.get("/auth/yo", headers={"Authorization": "Bearer token.falso.invalido"}).status_code == 401


@prueba("PF-15", "Verificación de coordinación: el cierre rechazado devuelve el reporte a atención",
        requisito="RF-11", ca="CA-05")
def test_pf15_verificacion_rechazada(cliente, datos):
    rid = reporte_en_atencion(cliente, datos, "alta")
    cierre = cliente.post(f"/reportes/{rid}/finalizar", headers=datos.h.tec1, json=FINALIZAR)
    assert cierre.json()["estado"] == "en_verificacion"
    assert cliente.post(f"/reportes/{rid}/verificacion", headers=datos.h.tec1, json={"aprobado": True}).status_code == 403
    assert cliente.post(f"/reportes/{rid}/verificacion", headers=datos.h.coord, json={"aprobado": False}).status_code == 422
    r = cliente.post(f"/reportes/{rid}/verificacion", headers=datos.h.coord,
                     json={"aprobado": False, "comentario": "La lámpara sigue parpadeando"})
    assert r.json()["estado"] == "en_atencion" and r.json()["resultado_cierre"] is None
    # una falla que requiere un tercero se cierra con su motivo (siempre verificada por coordinación)
    otro = reporte_en_atencion(cliente, datos, "baja")
    sin_motivo = {"resultado": "requiere_tercero", "descripcion_solucion": "Se requiere proveedor externo"}
    assert cliente.post(f"/reportes/{otro}/finalizar", headers=datos.h.tec1, json=sin_motivo).status_code == 422
    r2 = cliente.post(f"/reportes/{otro}/finalizar", headers=datos.h.tec1,
                      json={**sin_motivo, "motivo": "Equipo bajo garantía del fabricante"})
    assert r2.json()["estado"] == "en_verificacion"
    cerrado = cliente.post(f"/reportes/{otro}/verificacion", headers=datos.h.coord, json={"aprobado": True}).json()
    assert cerrado["estado"] == "cerrado" and cerrado["motivo_cierre"] == "Equipo bajo garantía del fabricante"


@prueba("PF-16", "Reasignación: exige motivo, conserva el historial y respeta la disponibilidad",
        requisito="RF-09", ca="CA-03")
def test_pf16_reasignacion(cliente, datos):
    rid = crear_reporte(cliente, datos)
    evaluar_aceptar(cliente, datos, rid)
    asignar(cliente, datos, rid, "tec1")
    nueva = {"tecnico_id": datos.ids["tec2"]}
    assert cliente.post(f"/reportes/{rid}/asignaciones", headers=datos.h.coord, json=nueva).status_code == 422
    assert cliente.post(f"/reportes/{rid}/asignaciones", headers=datos.h.coord,
                        json={"tecnico_id": datos.ids["tec1"]}).status_code == 409
    # un técnico no disponible no puede recibir trabajo
    assert cliente.patch(f"/usuarios/{datos.ids['tec2']}", headers=datos.h.coord, json={"disponible": False}).status_code == 200
    assert cliente.post(f"/reportes/{rid}/asignaciones", headers=datos.h.coord,
                        json={**nueva, "motivo": "Mayor experiencia"}).status_code == 409
    cliente.patch(f"/usuarios/{datos.ids['tec2']}", headers=datos.h.coord, json={"disponible": True})
    ok = cliente.post(f"/reportes/{rid}/asignaciones", headers=datos.h.coord, json={**nueva, "motivo": "Mayor experiencia"})
    assert ok.status_code == 201
    detalle = cliente.get(f"/reportes/{rid}", headers=datos.h.coord).json()
    assert [(a["tecnico"]["nombre"], a["activa"]) for a in detalle["asignaciones"]] == [
        ("Técnico Uno", False), ("Técnico Dos", True)]
    assert cliente.get("/reportes", headers=datos.h.tec1).json() == []        # ya no lo ve
    assert cliente.post(f"/reportes/{rid}/intervenciones", headers=datos.h.tec1, json={
        "fecha_intervencion": HOY, "actividades": "Intento sin asignación", "tiempo_minutos": 5, "resultado": "N/A"}).status_code == 403


@prueba("PF-17", "Cada perfil ve únicamente su información", requisito="RF-05, RNF-01", ca="CA-01, CA-03")
def test_pf17_visibilidad_por_perfil(cliente, datos):
    de_doc = crear_reporte(cliente, datos, "doc")
    de_adm = crear_reporte(cliente, datos, "adm")
    assert [x["id"] for x in cliente.get("/reportes", headers=datos.h.doc).json()] == [de_doc]
    assert cliente.get(f"/reportes/{de_adm}", headers=datos.h.doc).status_code == 403
    assert cliente.get(f"/reportes/{de_adm}/historial", headers=datos.h.tec1).status_code == 403
    assert len(cliente.get("/reportes", headers=datos.h.coord).json()) == 2


@prueba("PF-18", "Fotografías: formato y contenido válidos; archivos no permitidos se rechazan",
        requisito="RF-04, RNF-02", ca="CA-01")
def test_pf18_fotografias(cliente, datos):
    rid = crear_reporte(cliente, datos)
    jpg = b"\xff\xd8\xff\xe0" + b"1" * 32
    subir = lambda nombre, contenido, tipo, quien="doc": cliente.post(  # noqa: E731
        f"/reportes/{rid}/fotos", headers=getattr(datos.h, quien),
        files={"archivo": (nombre, io.BytesIO(contenido), tipo)})
    assert subir("foto.jpg", jpg, "image/jpeg").status_code == 201
    assert subir("script.exe", b"MZ" + b"0" * 20, "application/octet-stream").status_code == 422
    assert subir("falsa.png", b"esto no es una imagen", "image/png").status_code == 422
    assert subir("foto.jpg", jpg, "image/jpeg", "adm").status_code == 403       # no es su reporte
    assert len(cliente.get(f"/reportes/{rid}", headers=datos.h.doc).json()["fotos"]) == 1


@prueba("PF-19", "Coordinación mantiene el catálogo de espacios; los reportantes solo lo consultan",
        requisito="RF-02", ca="CA-01")
def test_pf19_catalogo_de_espacios(cliente, datos):
    assert len(cliente.get("/espacios", headers=datos.h.doc).json()) == 3
    edificio = cliente.get("/edificios", headers=datos.h.doc).json()[0]["id"]
    nuevo = {"edificio_id": edificio, "nombre": "Sala de profesores", "tipo": "oficina", "piso": "2"}
    assert cliente.post("/espacios", headers=datos.h.doc, json=nuevo).status_code == 403
    creado = cliente.post("/espacios", headers=datos.h.coord, json=nuevo)
    assert creado.status_code == 201
    assert cliente.post("/espacios", headers=datos.h.coord, json=nuevo).status_code == 409
    assert cliente.post("/espacios", headers=datos.h.coord, json={**nuevo, "edificio_id": 999}).status_code == 404
    eid = creado.json()["id"]
    assert cliente.patch(f"/espacios/{eid}", headers=datos.h.coord, json={"nombre": "Sala docentes"}).json()["nombre"] == "Sala docentes"
    # un espacio desactivado ya no admite reportes nuevos
    cliente.patch(f"/espacios/{eid}", headers=datos.h.coord, json={"activo": False})
    r = cliente.post("/reportes", headers=datos.h.doc, json={"espacio_id": eid, "descripcion": "Falla en espacio inactivo",
                                                            "fecha_inicio_falla": AYER})
    assert r.status_code == 422
