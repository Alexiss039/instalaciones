# Evidencias de las pruebas funcionales de la API

Generado automáticamente con `EVIDENCIAS=1 pytest` el 2026-11-19 17:00.

| ID | Prueba | Requisito | CA | Resultado |
|---|---|---|---|---|
| PF-01 | Registrar un reporte válido vinculado a un espacio y comprobar que persiste | RF-03, RF-05 | CA-01 | APROBADA |
| PF-02 | Rechazar reportes con datos obligatorios faltantes o inválidos sin crear registros | RF-03, RNF-02 | CA-01 | APROBADA |
| PF-03 | Consultar el listado de reportes y el detalle de un reporte | RF-05 | CA-01 | APROBADA |
| PF-04 | Consultar un reporte inexistente y recibir un error HTTP controlado | RNF-02 | CA-01 | APROBADA |
| PF-05 | Evaluar un reporte (aceptar con prioridad / rechazar con motivo) y registrar la decisión | RF-06 | CA-02 | APROBADA |
| PF-06 | Rechazar transiciones de estado no permitidas | RF-08 | CA-02 | APROBADA |
| PF-07 | Asignar un responsable autorizado y comprobar su persistencia y visibilidad | RF-09, RF-05 | CA-03 | APROBADA |
| PF-08 | Bloquear gestiones de usuarios no autorizados sin modificar datos | RNF-01 | CA-02, CA-03 | APROBADA |
| PF-09 | Registrar una intervención válida vinculada al reporte | RF-10 | CA-04 | APROBADA |
| PF-10 | Cerrar un reporte y consultar el resultado del cierre con su historial | RF-11, RF-08 | CA-05 | APROBADA |
| PF-11 | Consultar el dashboard con conteos y filtros coherentes | RF-12 | CA-06 | APROBADA |
| PF-12 | Flujo completo por API: reporte, foto, valoración, evaluación, asignación, intervención, verificación y cierre | RF-03 a RF-12 | CA-01 a CA-06 | APROBADA |
| PF-13 | Reportes duplicados: se vinculan al original y se conservan todos los reportantes | RF-07 | CA-02 | APROBADA |
| PF-14 | Autenticación: registro, credenciales incorrectas y correo repetido | RF-01, RNF-03 | CA-01 | APROBADA |
| PF-15 | Verificación de coordinación: el cierre rechazado devuelve el reporte a atención | RF-11 | CA-05 | APROBADA |
| PF-16 | Reasignación: exige motivo, conserva el historial y respeta la disponibilidad | RF-09 | CA-03 | APROBADA |
| PF-17 | Cada perfil ve únicamente su información | RF-05, RNF-01 | CA-01, CA-03 | APROBADA |
| PF-18 | Fotografías: formato y contenido válidos; archivos no permitidos se rechazan | RF-04, RNF-02 | CA-01 | APROBADA |
| PF-19 | Coordinación mantiene el catálogo de espacios; los reportantes solo lo consultan | RF-02 | CA-01 | APROBADA |

## PF-01 - Registrar un reporte válido vinculado a un espacio y comprobar que persiste

- **Requisito:** RF-03, RF-05  |  **Criterio:** CA-01
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada.
- **Resultado esperado:** HTTP 201 con estado «reportado»; el reporte se puede consultar después con los mismos datos.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "El proyector del aula no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "electrica", "urgencia_reportada": "alta"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "electrica", "descripcion": "El proyector del aula no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.179083", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": "alta", "requiere_verificacion": false, "motivo_rechazo": null…`
2. `GET /reportes/1` como *reportante (docente)* → **HTTP 200**
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "electrica", "descripcion": "El proyector del aula no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.179083", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": "alta", "requiere_verificacion": false, "motivo_rechazo": null…`

## PF-02 - Rechazar reportes con datos obligatorios faltantes o inválidos sin crear registros

- **Requisito:** RF-03, RNF-02  |  **Criterio:** CA-01
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada.
- **Resultado esperado:** HTTP 422 con el detalle de cada campo inválido; no se crea ningún reporte.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 422**
   - Entrada: `{"espacio_id": 1, "fecha_inicio_falla": "2026-11-18"}`
   - Respuesta: `{"detalle": "Datos inválidos", "codigo": 422, "errores": [{"campo": "descripcion", "mensaje": "Field required"}]}`
2. `POST /reportes` como *reportante (docente)* → **HTTP 422**
   - Entrada: `{"espacio_id": 1, "descripcion": "corta", "fecha_inicio_falla": "2026-11-18"}`
   - Respuesta: `{"detalle": "Datos inválidos", "codigo": 422, "errores": [{"campo": "descripcion", "mensaje": "String should have at least 10 characters"}]}`
3. `POST /reportes` como *reportante (docente)* → **HTTP 422**
   - Entrada: `{"espacio_id": 1, "descripcion": "Descripción suficiente", "fecha_inicio_falla": "2026-11-22"}`
   - Respuesta: `{"detalle": "Datos inválidos", "codigo": 422, "errores": [{"campo": "fecha_inicio_falla", "mensaje": "Value error, La fecha no puede ser futura"}]}`
4. `POST /reportes` como *reportante (docente)* → **HTTP 422**
   - Entrada: `{"espacio_id": 1, "descripcion": "Descripción suficiente", "fecha_inicio_falla": "no-es-fecha"}`
   - Respuesta: `{"detalle": "Datos inválidos", "codigo": 422, "errores": [{"campo": "fecha_inicio_falla", "mensaje": "Input should be a valid date or datetime, invalid character in year"}]}`
5. `POST /reportes` como *reportante (docente)* → **HTTP 422**
   - Entrada: `{"espacio_id": 1, "descripcion": "Descripción suficiente", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "inventada"}`
   - Respuesta: `{"detalle": "Datos inválidos", "codigo": 422, "errores": [{"campo": "tipo_falla", "mensaje": "Input should be 'electrica', 'iluminacion', 'plomeria', 'climatizacion', 'mobiliario', 'red_datos', 'estructura' or 'otra'"}]}`
6. `POST /reportes` como *reportante (docente)* → **HTTP 422**
   - Entrada: `{"espacio_id": 99999, "descripcion": "Descripción suficiente", "fecha_inicio_falla": "2026-11-18"}`
   - Respuesta: `{"detalle": "El espacio indicado no existe o está inactivo", "codigo": 422}`
7. `GET /reportes` como *coordinación* → **HTTP 200**
   - Respuesta: `[]`

## PF-03 - Consultar el listado de reportes y el detalle de un reporte

- **Requisito:** RF-05  |  **Criterio:** CA-01
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada + 3 reportes creados por el docente.
- **Resultado esperado:** Coordinación recibe HTTP 200 con los 3 reportes del más reciente al más antiguo; el detalle trae edificio, espacio y teléfono del reportante.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "Falla número 0 en el aula", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "Falla número 0 en el aula", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.453019", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null, "resul…`
2. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "Falla número 1 en el aula", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "Falla número 1 en el aula", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.478649", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null, "resul…`
3. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "Falla número 2 en el aula", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 3, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "Falla número 2 en el aula", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.491338", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null, "resul…`
4. `GET /reportes` como *coordinación* → **HTTP 200**
   - Respuesta: `[{"id": 3, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "Falla número 2 en el aula", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.491338", "creador": {"id": 4, "nombre": "Docente Prueba"}, "grupo": "pendiente"}, {"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A"…`
5. `GET /reportes/1` como *coordinación* → **HTTP 200**
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "Falla número 0 en el aula", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.453019", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null, "resul…`

## PF-04 - Consultar un reporte inexistente y recibir un error HTTP controlado

- **Requisito:** RNF-02  |  **Criterio:** CA-01
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada.
- **Resultado esperado:** HTTP 404 con mensaje y código de error controlados, sin excepción del servidor.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `GET /reportes/99999` como *coordinación* → **HTTP 404**
   - Respuesta: `{"detalle": "Reporte no encontrado", "codigo": 404}`

## PF-05 - Evaluar un reporte (aceptar con prioridad / rechazar con motivo) y registrar la decisión

- **Requisito:** RF-06  |  **Criterio:** CA-02
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada + reportes en estado «reportado».
- **Resultado esperado:** Aceptar: estado «evaluado» con prioridad. Rechazar con motivo: estado «rechazado». Ambas decisiones quedan en el historial.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.698627", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
2. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "Solicito pintar toda la fachada del edificio", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "Solicito pintar toda la fachada del edificio", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.723271", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rec…`
3. `POST /reportes/1/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "aceptar", "prioridad": "alta"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "alta", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.698627", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": true, "motivo_rechazo": null,…`
4. `POST /reportes/2/evaluacion` como *coordinación* → **HTTP 422**
   - Entrada: `{"decision": "rechazar"}`
   - Respuesta: `{"detalle": "Datos inválidos", "codigo": 422, "errores": [{"campo": "body", "mensaje": "Value error, Para rechazar un reporte debe indicar el motivo"}]}`
5. `POST /reportes/2/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "rechazar", "motivo": "No corresponde a las instalaciones"}`
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "Solicito pintar toda la fachada del edificio", "fecha_inicio_falla": "2026-11-18", "estado": "rechazado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.723271", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rec…`
6. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 3, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.780948", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
7. `POST /reportes/3/evaluacion` como *coordinación* → **HTTP 422**
   - Entrada: `{"decision": "aceptar"}`
   - Respuesta: `{"detalle": "Datos inválidos", "codigo": 422, "errores": [{"campo": "body", "mensaje": "Value error, Para aceptar un reporte debe definir la prioridad"}]}`

## PF-06 - Rechazar transiciones de estado no permitidas

- **Requisito:** RF-08  |  **Criterio:** CA-02
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada + reporte recién creado (estado «reportado»).
- **Resultado esperado:** Asignar o finalizar antes de evaluar da HTTP 409; rechazar un reporte ya evaluado da HTTP 409 y el estado se mantiene «evaluado».
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.887233", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
2. `POST /reportes/1/asignaciones` como *coordinación* → **HTTP 409**
   - Entrada: `{"tecnico_id": 2}`
   - Respuesta: `{"detalle": "No se puede asignar responsables a un reporte en estado 'reportado' (estados válidos: evaluado, asignado, en_atencion)", "codigo": 409}`
3. `POST /reportes/1/finalizar` como *coordinación* → **HTTP 409**
   - Entrada: `{"resultado": "resuelto", "descripcion_solucion": "Se reemplazó la lámpara defectuosa"}`
   - Respuesta: `{"detalle": "No se puede finalizar un reporte en estado 'reportado' (estados válidos: en_atencion)", "codigo": 409}`
4. `POST /reportes/1/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "aceptar", "prioridad": "media"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.887233", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": nul…`
5. `POST /reportes/1/evaluacion` como *coordinación* → **HTTP 409**
   - Entrada: `{"decision": "rechazar", "motivo": "Intento de rechazo tardío"}`
   - Respuesta: `{"detalle": "No se puede evaluar un reporte en estado 'evaluado' (estados válidos: reportado)", "codigo": 409}`
6. `GET /reportes/1` como *coordinación* → **HTTP 200**
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:36.887233", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": nul…`

## PF-07 - Asignar un responsable autorizado y comprobar su persistencia y visibilidad

- **Requisito:** RF-09, RF-05  |  **Criterio:** CA-03
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada + reporte evaluado.
- **Resultado esperado:** HTTP 201; el reporte pasa a «asignado» y el técnico responsable lo ve en su lista.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.053868", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
2. `POST /reportes/1/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "aceptar", "prioridad": "media"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.053868", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": nul…`
3. `POST /reportes/1/asignaciones` como *coordinación* → **HTTP 201**
   - Entrada: `{"tecnico_id": 2}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "rol": "responsable", "activa": true, "motivo": null, "fecha_asignacion": "2026-11-19T22:00:37.106615", "fecha_retiro": null, "motivo_retiro": null}`
4. `GET /reportes/1` como *coordinación* → **HTTP 200**
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "asignado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.053868", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": nul…`
5. `GET /reportes` como *mantenimiento (Técnico Uno)* → **HTTP 200**
   - Respuesta: `[{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "asignado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.053868", "creador": {"id": 4, "nombre": "Docente Prueba"}, "grupo": "pendiente"}]`
6. `GET /reportes` como *mantenimiento (Técnico Dos)* → **HTTP 200**
   - Respuesta: `[]`
7. `GET /tecnicos` como *coordinación* → **HTTP 200**
   - Parámetros: `{"tipo_falla": "iluminacion"}`
   - Respuesta: `[{"id": 3, "nombre": "Técnico Dos", "especialidades": ["plomeria"], "experiencia_anios": 2, "disponible": true, "trabajos_pendientes": 0, "coincide_especialidad": false}, {"id": 2, "nombre": "Técnico Uno", "especialidades": ["electrica"], "experiencia_anios": 6, "disponible": true, "trabajos_pendientes": 1, "coincide_especialidad": false}]`

## PF-08 - Bloquear gestiones de usuarios no autorizados sin modificar datos

- **Requisito:** RNF-01  |  **Criterio:** CA-02, CA-03
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada + reporte en estado «reportado».
- **Resultado esperado:** HTTP 401 sin sesión y HTTP 403 para docente o técnico en evaluación, asignación, dashboard y usuarios; el reporte queda sin prioridad ni asignaciones.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.244926", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
2. `POST /reportes/1/evaluacion` como *reportante (docente)* → **HTTP 403**
   - Entrada: `{"decision": "aceptar", "prioridad": "alta"}`
   - Respuesta: `{"detalle": "Su perfil no tiene permiso para realizar esta acción", "codigo": 403}`
3. `POST /reportes/1/evaluacion` como *mantenimiento (Técnico Uno)* → **HTTP 403**
   - Entrada: `{"decision": "aceptar", "prioridad": "alta"}`
   - Respuesta: `{"detalle": "Su perfil no tiene permiso para realizar esta acción", "codigo": 403}`
4. `POST /reportes/1/evaluacion` como *sin sesión* → **HTTP 401**
   - Entrada: `{"decision": "aceptar", "prioridad": "alta"}`
   - Respuesta: `{"detalle": "Credenciales no válidas o sesión expirada", "codigo": 401}`
5. `POST /reportes/1/asignaciones` como *mantenimiento (Técnico Uno)* → **HTTP 403**
   - Entrada: `{"tecnico_id": 2}`
   - Respuesta: `{"detalle": "Su perfil no tiene permiso para realizar esta acción", "codigo": 403}`
6. `GET /dashboard/resumen` como *reportante (docente)* → **HTTP 403**
   - Respuesta: `{"detalle": "Su perfil no tiene permiso para realizar esta acción", "codigo": 403}`
7. `GET /usuarios` como *mantenimiento (Técnico Uno)* → **HTTP 403**
   - Respuesta: `{"detalle": "Su perfil no tiene permiso para realizar esta acción", "codigo": 403}`
8. `GET /reportes/1` como *coordinación* → **HTTP 200**
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.244926", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`

## PF-09 - Registrar una intervención válida vinculada al reporte

- **Requisito:** RF-10  |  **Criterio:** CA-04
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada + reporte asignado al técnico.
- **Resultado esperado:** HTTP 201; la intervención queda vinculada al reporte y el estado pasa a «en atención».
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.416967", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
2. `POST /reportes/1/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "aceptar", "prioridad": "media"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.416967", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": nul…`
3. `POST /reportes/1/asignaciones` como *coordinación* → **HTTP 201**
   - Entrada: `{"tecnico_id": 2}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "rol": "responsable", "activa": true, "motivo": null, "fecha_asignacion": "2026-11-19T22:00:37.491301", "fecha_retiro": null, "motivo_retiro": null}`
4. `POST /reportes/1/intervenciones` como *mantenimiento (Técnico Uno)* → **HTTP 201**
   - Entrada: `{"fecha_intervencion": "2026-11-19", "actividades": "Diagnóstico del circuito de iluminación", "tiempo_minutos": 30, "resultado": "Se identificó el balastro dañado"}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "fecha_intervencion": "2026-11-19", "actividades": "Diagnóstico del circuito de iluminación", "tiempo_minutos": 30, "resultado": "Se identificó el balastro dañado", "registrado_en": "2026-11-19T22:00:37.504610"}`
5. `GET /reportes/1` como *coordinación* → **HTTP 200**
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "en_atencion", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.416967", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": …`
6. `POST /reportes/1/intervenciones` como *mantenimiento (Técnico Dos)* → **HTTP 403**
   - Entrada: `{"fecha_intervencion": "2026-11-19", "actividades": "Actividad de prueba", "tiempo_minutos": 10, "resultado": "Sin novedad"}`
   - Respuesta: `{"detalle": "No tiene acceso a este reporte", "codigo": 403}`
7. `POST /reportes/1/intervenciones` como *mantenimiento (Técnico Uno)* → **HTTP 422**
   - Entrada: `{"fecha_intervencion": "2026-11-19", "actividades": "Actividad de prueba", "tiempo_minutos": 0, "resultado": "Sin novedad"}`
   - Respuesta: `{"detalle": "Datos inválidos", "codigo": 422, "errores": [{"campo": "tiempo_minutos", "mensaje": "Input should be greater than or equal to 1"}]}`
8. `POST /reportes/1/intervenciones` como *mantenimiento (Técnico Uno)* → **HTTP 422**
   - Entrada: `{"fecha_intervencion": "2000-01-01", "actividades": "Actividad de prueba", "tiempo_minutos": 10, "resultado": "Sin novedad"}`
   - Respuesta: `{"detalle": "La fecha de la intervención no puede ser anterior al inicio de la falla", "codigo": 422}`
9. `GET /reportes/1/intervenciones` como *mantenimiento (Técnico Uno)* → **HTTP 200**
   - Respuesta: `[{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "fecha_intervencion": "2026-11-19", "actividades": "Diagnóstico del circuito de iluminación", "tiempo_minutos": 30, "resultado": "Se identificó el balastro dañado", "registrado_en": "2026-11-19T22:00:37.504610"}]`

## PF-10 - Cerrar un reporte y consultar el resultado del cierre con su historial

- **Requisito:** RF-11, RF-08  |  **Criterio:** CA-05
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada + reporte en atención con una intervención registrada.
- **Resultado esperado:** Estado «cerrado» con resultado y descripción de la solución; el historial muestra todas las transiciones.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.639645", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
2. `POST /reportes/1/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "aceptar", "prioridad": "media"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.639645", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": nul…`
3. `POST /reportes/1/asignaciones` como *coordinación* → **HTTP 201**
   - Entrada: `{"tecnico_id": 2}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "rol": "responsable", "activa": true, "motivo": null, "fecha_asignacion": "2026-11-19T22:00:37.687613", "fecha_retiro": null, "motivo_retiro": null}`
4. `POST /reportes/1/finalizar` como *mantenimiento (Técnico Uno)* → **HTTP 409**
   - Entrada: `{"resultado": "resuelto", "descripcion_solucion": "Se reemplazó la lámpara defectuosa"}`
   - Respuesta: `{"detalle": "No se puede finalizar un reporte en estado 'asignado' (estados válidos: en_atencion)", "codigo": 409}`
5. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.708337", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
6. `POST /reportes/2/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "aceptar", "prioridad": "media"}`
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.708337", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": nul…`
7. `POST /reportes/2/asignaciones` como *coordinación* → **HTTP 201**
   - Entrada: `{"tecnico_id": 2}`
   - Respuesta: `{"id": 2, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "rol": "responsable", "activa": true, "motivo": null, "fecha_asignacion": "2026-11-19T22:00:37.734640", "fecha_retiro": null, "motivo_retiro": null}`
8. `POST /reportes/2/intervenciones` como *mantenimiento (Técnico Uno)* → **HTTP 201**
   - Entrada: `{"fecha_intervencion": "2026-11-19", "actividades": "Cambio de la lámpara y revisión del circuito", "tiempo_minutos": 45, "resultado": "Iluminación restablecida"}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "fecha_intervencion": "2026-11-19", "actividades": "Cambio de la lámpara y revisión del circuito", "tiempo_minutos": 45, "resultado": "Iluminación restablecida", "registrado_en": "2026-11-19T22:00:37.746838"}`
9. `POST /reportes/2/finalizar` como *mantenimiento (Técnico Uno)* → **HTTP 200**
   - Entrada: `{"resultado": "resuelto", "descripcion_solucion": "Se reemplazó la lámpara defectuosa"}`
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "cerrado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.708337", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null…`
10. `GET /reportes/2` como *reportante (docente)* → **HTTP 200**
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "cerrado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.708337", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null…`
11. `POST /reportes/2/finalizar` como *mantenimiento (Técnico Uno)* → **HTTP 409**
   - Entrada: `{"resultado": "resuelto", "descripcion_solucion": "Se reemplazó la lámpara defectuosa"}`
   - Respuesta: `{"detalle": "No se puede finalizar un reporte en estado 'cerrado' (estados válidos: en_atencion)", "codigo": 409}`

## PF-11 - Consultar el dashboard con conteos y filtros coherentes

- **Requisito:** RF-12  |  **Criterio:** CA-06
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada + reportes en distintos estados, prioridades y tipos.
- **Resultado esperado:** Los conteos del dashboard coinciden con los reportes creados y los filtros reducen el resultado de forma coherente.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "electrica"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "electrica", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.867502", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null, "…`
2. `POST /reportes` como *reportante (administrativo)* → **HTTP 201**
   - Entrada: `{"espacio_id": 2, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "electrica"}`
   - Respuesta: `{"id": 2, "espacio": {"id": 2, "nombre": "Laboratorio 1", "tipo": "laboratorio", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "electrica", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.892485", "creador": {"id": 5, "nombre": "Administrativo Prueba", "correo": "adm@prueba.test", "telefono": "3001112233", "cargo": "administrativo"}, "urgencia_reportada": null, "requiere_verificacion": false,…`
3. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "plomeria"}`
   - Respuesta: `{"id": 3, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "plomeria", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.904394", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null, "r…`
4. `POST /reportes/1/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "aceptar", "prioridad": "media"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "electrica", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.867502", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
5. `POST /reportes/1/asignaciones` como *coordinación* → **HTTP 201**
   - Entrada: `{"tecnico_id": 2}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "rol": "responsable", "activa": true, "motivo": null, "fecha_asignacion": "2026-11-19T22:00:37.941256", "fecha_retiro": null, "motivo_retiro": null}`
6. `POST /reportes/1/intervenciones` como *mantenimiento (Técnico Uno)* → **HTTP 201**
   - Entrada: `{"fecha_intervencion": "2026-11-19", "actividades": "Cambio de la lámpara y revisión del circuito", "tiempo_minutos": 45, "resultado": "Iluminación restablecida"}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "fecha_intervencion": "2026-11-19", "actividades": "Cambio de la lámpara y revisión del circuito", "tiempo_minutos": 45, "resultado": "Iluminación restablecida", "registrado_en": "2026-11-19T22:00:37.953718"}`
7. `GET /dashboard/resumen` como *coordinación* → **HTTP 200**
   - Respuesta: `{"desde": null, "hasta": null, "total_reportes": 3, "por_grupo": [{"clave": "pendiente", "etiqueta": "pendiente", "total": 2}, {"clave": "en_atencion", "etiqueta": "en_atencion", "total": 1}], "por_estado": [{"clave": "reportado", "etiqueta": "reportado", "total": 2}, {"clave": "en_atencion", "etiqueta": "en_atencion", "total": 1}], "fallas_mas_frecuentes": [{"clave": "electrica", "etiqueta": "electrica", "total": 2}, {"clave": "plomeria", "etiqueta": "plomeria", "total": 1}], "espacios_afectados": [{"clave": "1", "etiqueta": "Bloque A - Aula 101", "total": 2}, {"clave": "2", "etiqueta": "Bloq…`
8. `GET /dashboard/resumen` como *coordinación* → **HTTP 200**
   - Parámetros: `{"desde": "2026-11-19", "hasta": "2026-11-19"}`
   - Respuesta: `{"desde": "2026-11-19", "hasta": "2026-11-19", "total_reportes": 3, "por_grupo": [{"clave": "pendiente", "etiqueta": "pendiente", "total": 2}, {"clave": "en_atencion", "etiqueta": "en_atencion", "total": 1}], "por_estado": [{"clave": "reportado", "etiqueta": "reportado", "total": 2}, {"clave": "en_atencion", "etiqueta": "en_atencion", "total": 1}], "fallas_mas_frecuentes": [{"clave": "electrica", "etiqueta": "electrica", "total": 2}, {"clave": "plomeria", "etiqueta": "plomeria", "total": 1}], "espacios_afectados": [{"clave": "1", "etiqueta": "Bloque A - Aula 101", "total": 2}, {"clave": "2", "…`
9. `GET /dashboard/resumen` como *coordinación* → **HTTP 200**
   - Parámetros: `{"desde": "2026-11-24"}`
   - Respuesta: `{"desde": "2026-11-24", "hasta": null, "total_reportes": 0, "por_grupo": [], "por_estado": [], "fallas_mas_frecuentes": [], "espacios_afectados": [], "por_responsable": [], "por_resultado_cierre": []}`
10. `GET /dashboard/resumen` como *coordinación* → **HTTP 422**
   - Parámetros: `{"desde": "2026-11-24", "hasta": "2026-11-19"}`
   - Respuesta: `{"detalle": "La fecha 'desde' no puede ser posterior a 'hasta'", "codigo": 422}`
11. `GET /reportes` como *coordinación* → **HTTP 200**
   - Parámetros: `{"grupo": "pendiente", "tipo_falla": "electrica"}`
   - Respuesta: `[{"id": 2, "espacio": {"id": 2, "nombre": "Laboratorio 1", "tipo": "laboratorio", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "electrica", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:37.892485", "creador": {"id": 5, "nombre": "Administrativo Prueba"}, "grupo": "pendiente"}]`

## PF-12 - Flujo completo por API: reporte, foto, valoración, evaluación, asignación, intervención, verificación y cierre

- **Requisito:** RF-03 a RF-12  |  **Criterio:** CA-01 a CA-06
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada.
- **Resultado esperado:** Todo el recorrido responde sin error y el reporte termina «cerrado» con su historial completo.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "electrica", "urgencia_reportada": "alta"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "electrica", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.110605", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": "alta", "requiere_verificacion": false, "motivo_rechazo": null,…`
2. `POST /reportes/1/fotos` como *reportante (docente)* → **HTTP 201**
   - Entrada: `"(archivo adjunto)"`
   - Respuesta: `{"id": 1, "nombre_original": "falla.png", "tipo_contenido": "image/png", "tamano_bytes": 72, "subido_en": "2026-11-19T22:00:38.142541"}`
3. `POST /reportes/1/valoraciones` como *coordinación* → **HTTP 201**
   - Entrada: `{"tecnico_id": 2, "indicaciones": "Revisar si es falla eléctrica"}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "indicaciones": "Revisar si es falla eléctrica", "fecha_solicitud": "2026-11-19T22:00:38.153833", "concepto": null, "fecha_respuesta": null}`
4. `GET /reportes` como *mantenimiento (Técnico Uno)* → **HTTP 200**
   - Respuesta: `[{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "electrica", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.110605", "creador": {"id": 4, "nombre": "Docente Prueba"}, "grupo": "pendiente"}]`
5. `POST /reportes/1/valoraciones/1/respuesta` como *mantenimiento (Técnico Uno)* → **HTTP 200**
   - Entrada: `{"concepto": "Falla en el tablero, requiere intervención eléctrica"}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "indicaciones": "Revisar si es falla eléctrica", "fecha_solicitud": "2026-11-19T22:00:38.153833", "concepto": "Falla en el tablero, requiere intervención eléctrica", "fecha_respuesta": "2026-11-19T22:00:38.180113"}`
6. `POST /reportes/1/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "aceptar", "prioridad": "alta"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "electrica", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "alta", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.110605", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": "alta", "requiere_verificacion": true, "motivo_rechazo": null,…`
7. `POST /reportes/1/asignaciones` como *coordinación* → **HTTP 201**
   - Entrada: `{"tecnico_id": 2}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "rol": "responsable", "activa": true, "motivo": null, "fecha_asignacion": "2026-11-19T22:00:38.210122", "fecha_retiro": null, "motivo_retiro": null}`
8. `POST /reportes/1/asignaciones` como *coordinación* → **HTTP 201**
   - Entrada: `{"tecnico_id": 3, "rol": "apoyo"}`
   - Respuesta: `{"id": 2, "tecnico": {"id": 3, "nombre": "Técnico Dos"}, "rol": "apoyo", "activa": true, "motivo": null, "fecha_asignacion": "2026-11-19T22:00:38.221954", "fecha_retiro": null, "motivo_retiro": null}`
9. `POST /reportes/1/intervenciones` como *mantenimiento (Técnico Uno)* → **HTTP 201**
   - Entrada: `{"fecha_intervencion": "2026-11-19", "actividades": "Cambio de la lámpara y revisión del circuito", "tiempo_minutos": 45, "resultado": "Iluminación restablecida"}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "fecha_intervencion": "2026-11-19", "actividades": "Cambio de la lámpara y revisión del circuito", "tiempo_minutos": 45, "resultado": "Iluminación restablecida", "registrado_en": "2026-11-19T22:00:38.234446"}`
10. `POST /reportes/1/intervenciones` como *mantenimiento (Técnico Dos)* → **HTTP 201**
   - Entrada: `{"fecha_intervencion": "2026-11-19", "actividades": "Apoyo en el cableado del tablero", "tiempo_minutos": 45, "resultado": "Iluminación restablecida"}`
   - Respuesta: `{"id": 2, "tecnico": {"id": 3, "nombre": "Técnico Dos"}, "fecha_intervencion": "2026-11-19", "actividades": "Apoyo en el cableado del tablero", "tiempo_minutos": 45, "resultado": "Iluminación restablecida", "registrado_en": "2026-11-19T22:00:38.244789"}`
11. `POST /reportes/1/finalizar` como *mantenimiento (Técnico Uno)* → **HTTP 200**
   - Entrada: `{"resultado": "resuelto", "descripcion_solucion": "Se reemplazó la lámpara defectuosa"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "electrica", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "en_verificacion", "prioridad": "alta", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.110605", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": "alta", "requiere_verificacion": true, "motivo_rechazo"…`
12. `POST /reportes/1/verificacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"aprobado": true}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "electrica", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "cerrado", "prioridad": "alta", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.110605", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": "alta", "requiere_verificacion": true, "motivo_rechazo": null, …`
13. `GET /reportes/1` como *reportante (docente)* → **HTTP 200**
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "electrica", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "cerrado", "prioridad": "alta", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.110605", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": "alta", "requiere_verificacion": true, "motivo_rechazo": null, …`
14. `GET /reportes/1/fotos/1` como *coordinación* → **HTTP 200**
   - Respuesta: `"(image/png, 72 bytes)"`
15. `GET /dashboard/resumen` como *coordinación* → **HTTP 200**
   - Respuesta: `{"desde": null, "hasta": null, "total_reportes": 1, "por_grupo": [{"clave": "finalizado", "etiqueta": "finalizado", "total": 1}], "por_estado": [{"clave": "cerrado", "etiqueta": "cerrado", "total": 1}], "fallas_mas_frecuentes": [{"clave": "electrica", "etiqueta": "electrica", "total": 1}], "espacios_afectados": [{"clave": "1", "etiqueta": "Bloque A - Aula 101", "total": 1}], "por_responsable": [{"clave": "3", "etiqueta": "Técnico Dos", "total": 1}, {"clave": "2", "etiqueta": "Técnico Uno", "total": 1}], "por_resultado_cierre": [{"clave": "resuelto", "etiqueta": "resuelto", "total": 1}]}`

## PF-13 - Reportes duplicados: se vinculan al original y se conservan todos los reportantes

- **Requisito:** RF-07  |  **Criterio:** CA-02
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada + reporte original y reportes del mismo problema.
- **Resultado esperado:** Los duplicados quedan vinculados al original y todos los reportantes se conservan.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.421813", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
2. `POST /reportes` como *reportante (administrativo)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.449010", "creador": {"id": 5, "nombre": "Administrativo Prueba", "correo": "adm@prueba.test", "telefono": "3001112233", "cargo": "administrativo"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_r…`
3. `GET /reportes/2/posibles-duplicados` como *coordinación* → **HTTP 200**
   - Respuesta: `[{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.421813", "creador": {"id": 4, "nombre": "Docente Prueba"}, "grupo": "pendiente"}]`
4. `POST /reportes/2/evaluacion` como *coordinación* → **HTTP 422**
   - Entrada: `{"decision": "duplicado"}`
   - Respuesta: `{"detalle": "Datos inválidos", "codigo": 422, "errores": [{"campo": "body", "mensaje": "Value error, Para marcar un duplicado debe indicar el reporte original (duplicado_de_id)"}]}`
5. `POST /reportes/2/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "duplicado", "duplicado_de_id": 1}`
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "duplicado", "prioridad": null, "duplicado_de_id": 1, "creado_en": "2026-11-19T22:00:38.449010", "creador": {"id": 5, "nombre": "Administrativo Prueba", "correo": "adm@prueba.test", "telefono": "3001112233", "cargo": "administrativo"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rech…`
6. `POST /reportes/1/evaluacion` como *coordinación* → **HTTP 422**
   - Entrada: `{"decision": "duplicado", "duplicado_de_id": 1}`
   - Respuesta: `{"detalle": "El reporte original indicado no existe o es el mismo reporte", "codigo": 422}`
7. `POST /reportes/1/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "aceptar", "prioridad": "media"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.421813", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": nul…`
8. `GET /reportes/1` como *coordinación* → **HTTP 200**
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.421813", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": nul…`
9. `GET /reportes/2` como *reportante (administrativo)* → **HTTP 200**
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "duplicado", "prioridad": null, "duplicado_de_id": 1, "creado_en": "2026-11-19T22:00:38.449010", "creador": {"id": 5, "nombre": "Administrativo Prueba", "correo": "adm@prueba.test", "telefono": "3001112233", "cargo": "administrativo"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rech…`
10. `GET /dashboard/resumen` como *coordinación* → **HTTP 200**
   - Respuesta: `{"desde": null, "hasta": null, "total_reportes": 2, "por_grupo": [{"clave": "finalizado", "etiqueta": "finalizado", "total": 1}, {"clave": "pendiente", "etiqueta": "pendiente", "total": 1}], "por_estado": [{"clave": "duplicado", "etiqueta": "duplicado", "total": 1}, {"clave": "evaluado", "etiqueta": "evaluado", "total": 1}], "fallas_mas_frecuentes": [{"clave": "iluminacion", "etiqueta": "iluminacion", "total": 2}], "espacios_afectados": [{"clave": "1", "etiqueta": "Bloque A - Aula 101", "total": 2}], "por_responsable": [], "por_resultado_cierre": []}`

## PF-14 - Autenticación: registro, credenciales incorrectas y correo repetido

- **Requisito:** RF-01, RNF-03  |  **Criterio:** CA-01
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada.
- **Resultado esperado:** Registro HTTP 201 (rol reportante, sin devolver la contraseña); correo repetido 409; contraseña débil 422; login incorrecto 401; login correcto 200; token falso 401.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /auth/registro` como *sin sesión* → **HTTP 201**
   - Entrada: `{"nombre": "Docente Nuevo", "correo": "NUEVO@Prueba.test", "telefono": "3112223344", "password": "***", "cargo": "docente"}`
   - Respuesta: `{"id": 6, "nombre": "Docente Nuevo", "correo": "nuevo@prueba.test", "telefono": "3112223344", "rol": "reportante", "cargo": "docente", "especialidades": [], "experiencia_anios": 0, "disponible": true, "activo": true}`
2. `POST /auth/registro` como *sin sesión* → **HTTP 409**
   - Entrada: `{"nombre": "Docente Nuevo", "correo": "NUEVO@Prueba.test", "telefono": "3112223344", "password": "***", "cargo": "docente"}`
   - Respuesta: `{"detalle": "Ya existe un usuario con ese correo", "codigo": 409}`
3. `POST /auth/registro` como *sin sesión* → **HTTP 422**
   - Entrada: `{"nombre": "Docente Nuevo", "correo": "otro@prueba.test", "telefono": "3112223344", "password": "***", "cargo": "docente"}`
   - Respuesta: `{"detalle": "Datos inválidos", "codigo": 422, "errores": [{"campo": "password", "mensaje": "Value error, La contraseña debe tener al menos una letra y un número"}]}`
4. `POST /auth/login` como *sin sesión* → **HTTP 401**
   - Entrada: `{"username": "nuevo@prueba.test", "password": "***"}`
   - Respuesta: `{"detalle": "Correo o contraseña incorrectos", "codigo": 401}`
5. `POST /auth/login` como *sin sesión* → **HTTP 200**
   - Entrada: `{"username": "nuevo@prueba.test", "password": "***"}`
   - Respuesta: `{"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2IiwiZXhwIjoxNzk1MTU0NDM4fQ.ejcQ-v8Un67Rp1zYRjGV4-Y5mo1vb14AFqPKc6_pL5I", "token_type": "bearer", "usuario": {"id": 6, "nombre": "Docente Nuevo", "correo": "nuevo@prueba.test", "telefono": "3112223344", "rol": "reportante", "cargo": "docente", "especialidades": [], "experiencia_anios": 0, "disponible": true, "activo": true}}`
6. `GET /auth/yo` como *sin sesión* → **HTTP 200**
   - Respuesta: `{"id": 6, "nombre": "Docente Nuevo", "correo": "nuevo@prueba.test", "telefono": "3112223344", "rol": "reportante", "cargo": "docente", "especialidades": [], "experiencia_anios": 0, "disponible": true, "activo": true}`
7. `GET /auth/yo` como *sin sesión* → **HTTP 401**
   - Respuesta: `{"detalle": "Credenciales no válidas o sesión expirada", "codigo": 401}`

## PF-15 - Verificación de coordinación: el cierre rechazado devuelve el reporte a atención

- **Requisito:** RF-11  |  **Criterio:** CA-05
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada + reporte «en verificación».
- **Resultado esperado:** Si coordinación rechaza el cierre, el reporte vuelve a «en atención».
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.781383", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
2. `POST /reportes/1/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "aceptar", "prioridad": "alta"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "alta", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.781383", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": true, "motivo_rechazo": null,…`
3. `POST /reportes/1/asignaciones` como *coordinación* → **HTTP 201**
   - Entrada: `{"tecnico_id": 2}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "rol": "responsable", "activa": true, "motivo": null, "fecha_asignacion": "2026-11-19T22:00:38.829784", "fecha_retiro": null, "motivo_retiro": null}`
4. `POST /reportes/1/intervenciones` como *mantenimiento (Técnico Uno)* → **HTTP 201**
   - Entrada: `{"fecha_intervencion": "2026-11-19", "actividades": "Cambio de la lámpara y revisión del circuito", "tiempo_minutos": 45, "resultado": "Iluminación restablecida"}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "fecha_intervencion": "2026-11-19", "actividades": "Cambio de la lámpara y revisión del circuito", "tiempo_minutos": 45, "resultado": "Iluminación restablecida", "registrado_en": "2026-11-19T22:00:38.841964"}`
5. `POST /reportes/1/finalizar` como *mantenimiento (Técnico Uno)* → **HTTP 200**
   - Entrada: `{"resultado": "resuelto", "descripcion_solucion": "Se reemplazó la lámpara defectuosa"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "en_verificacion", "prioridad": "alta", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.781383", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": true, "motivo_rechazo"…`
6. `POST /reportes/1/verificacion` como *mantenimiento (Técnico Uno)* → **HTTP 403**
   - Entrada: `{"aprobado": true}`
   - Respuesta: `{"detalle": "Su perfil no tiene permiso para realizar esta acción", "codigo": 403}`
7. `POST /reportes/1/verificacion` como *coordinación* → **HTTP 422**
   - Entrada: `{"aprobado": false}`
   - Respuesta: `{"detalle": "Datos inválidos", "codigo": 422, "errores": [{"campo": "body", "mensaje": "Value error, Si no aprueba el cierre debe indicar el motivo en 'comentario'"}]}`
8. `POST /reportes/1/verificacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"aprobado": false, "comentario": "La lámpara sigue parpadeando"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "en_atencion", "prioridad": "alta", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.781383", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": true, "motivo_rechazo": nu…`
9. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.892955", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
10. `POST /reportes/2/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "aceptar", "prioridad": "baja"}`
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "baja", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.892955", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null…`
11. `POST /reportes/2/asignaciones` como *coordinación* → **HTTP 201**
   - Entrada: `{"tecnico_id": 2}`
   - Respuesta: `{"id": 2, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "rol": "responsable", "activa": true, "motivo": null, "fecha_asignacion": "2026-11-19T22:00:38.918671", "fecha_retiro": null, "motivo_retiro": null}`
12. `POST /reportes/2/intervenciones` como *mantenimiento (Técnico Uno)* → **HTTP 201**
   - Entrada: `{"fecha_intervencion": "2026-11-19", "actividades": "Cambio de la lámpara y revisión del circuito", "tiempo_minutos": 45, "resultado": "Iluminación restablecida"}`
   - Respuesta: `{"id": 2, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "fecha_intervencion": "2026-11-19", "actividades": "Cambio de la lámpara y revisión del circuito", "tiempo_minutos": 45, "resultado": "Iluminación restablecida", "registrado_en": "2026-11-19T22:00:38.931920"}`
13. `POST /reportes/2/finalizar` como *mantenimiento (Técnico Uno)* → **HTTP 422**
   - Entrada: `{"resultado": "requiere_tercero", "descripcion_solucion": "Se requiere proveedor externo"}`
   - Respuesta: `{"detalle": "Datos inválidos", "codigo": 422, "errores": [{"campo": "body", "mensaje": "Value error, Cuando la falla no queda resuelta debe indicar el motivo"}]}`
14. `POST /reportes/2/finalizar` como *mantenimiento (Técnico Uno)* → **HTTP 200**
   - Entrada: `{"resultado": "requiere_tercero", "descripcion_solucion": "Se requiere proveedor externo", "motivo": "Equipo bajo garantía del fabricante"}`
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "en_verificacion", "prioridad": "baja", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.892955", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo…`
15. `POST /reportes/2/verificacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"aprobado": true}`
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "cerrado", "prioridad": "baja", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:38.892955", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`

## PF-16 - Reasignación: exige motivo, conserva el historial y respeta la disponibilidad

- **Requisito:** RF-09  |  **Criterio:** CA-03
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada + reporte asignado.
- **Resultado esperado:** Reasignar sin motivo HTTP 422; con motivo se conserva el historial; un técnico no disponible se rechaza.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:39.059345", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
2. `POST /reportes/1/evaluacion` como *coordinación* → **HTTP 200**
   - Entrada: `{"decision": "aceptar", "prioridad": "media"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "evaluado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:39.059345", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": nul…`
3. `POST /reportes/1/asignaciones` como *coordinación* → **HTTP 201**
   - Entrada: `{"tecnico_id": 2}`
   - Respuesta: `{"id": 1, "tecnico": {"id": 2, "nombre": "Técnico Uno"}, "rol": "responsable", "activa": true, "motivo": null, "fecha_asignacion": "2026-11-19T22:00:39.107666", "fecha_retiro": null, "motivo_retiro": null}`
4. `POST /reportes/1/asignaciones` como *coordinación* → **HTTP 422**
   - Entrada: `{"tecnico_id": 3}`
   - Respuesta: `{"detalle": "Para cambiar el responsable debe indicar el motivo de la reasignación", "codigo": 422}`
5. `POST /reportes/1/asignaciones` como *coordinación* → **HTTP 409**
   - Entrada: `{"tecnico_id": 2}`
   - Respuesta: `{"detalle": "El técnico ya está asignado a este reporte", "codigo": 409}`
6. `PATCH /usuarios/3` como *coordinación* → **HTTP 200**
   - Entrada: `{"disponible": false}`
   - Respuesta: `{"id": 3, "nombre": "Técnico Dos", "correo": "tec2@prueba.test", "telefono": "3001112233", "rol": "mantenimiento", "cargo": null, "especialidades": ["plomeria"], "experiencia_anios": 2, "disponible": false, "activo": true}`
7. `POST /reportes/1/asignaciones` como *coordinación* → **HTTP 409**
   - Entrada: `{"tecnico_id": 3, "motivo": "Mayor experiencia"}`
   - Respuesta: `{"detalle": "El técnico no está disponible actualmente", "codigo": 409}`
8. `PATCH /usuarios/3` como *coordinación* → **HTTP 200**
   - Entrada: `{"disponible": true}`
   - Respuesta: `{"id": 3, "nombre": "Técnico Dos", "correo": "tec2@prueba.test", "telefono": "3001112233", "rol": "mantenimiento", "cargo": null, "especialidades": ["plomeria"], "experiencia_anios": 2, "disponible": true, "activo": true}`
9. `POST /reportes/1/asignaciones` como *coordinación* → **HTTP 201**
   - Entrada: `{"tecnico_id": 3, "motivo": "Mayor experiencia"}`
   - Respuesta: `{"id": 2, "tecnico": {"id": 3, "nombre": "Técnico Dos"}, "rol": "responsable", "activa": true, "motivo": "Mayor experiencia", "fecha_asignacion": "2026-11-19T22:00:39.167973", "fecha_retiro": null, "motivo_retiro": null}`
10. `GET /reportes/1` como *coordinación* → **HTTP 200**
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "asignado", "prioridad": "media", "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:39.059345", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": nul…`
11. `GET /reportes` como *mantenimiento (Técnico Uno)* → **HTTP 200**
   - Respuesta: `[]`
12. `POST /reportes/1/intervenciones` como *mantenimiento (Técnico Uno)* → **HTTP 403**
   - Entrada: `{"fecha_intervencion": "2026-11-19", "actividades": "Intento sin asignación", "tiempo_minutos": 5, "resultado": "N/A"}`
   - Respuesta: `{"detalle": "No tiene acceso a este reporte", "codigo": 403}`

## PF-17 - Cada perfil ve únicamente su información

- **Requisito:** RF-05, RNF-01  |  **Criterio:** CA-01, CA-03
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada + un reporte del docente y otro del administrativo.
- **Resultado esperado:** El docente ve solo el suyo (200) y recibe 403 al abrir el ajeno o su historial; coordinación ve ambos.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:39.288865", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
2. `POST /reportes` como *reportante (administrativo)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:39.313368", "creador": {"id": 5, "nombre": "Administrativo Prueba", "correo": "adm@prueba.test", "telefono": "3001112233", "cargo": "administrativo"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_r…`
3. `GET /reportes` como *reportante (docente)* → **HTTP 200**
   - Respuesta: `[{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:39.288865", "creador": {"id": 4, "nombre": "Docente Prueba"}, "grupo": "pendiente"}]`
4. `GET /reportes/2` como *reportante (docente)* → **HTTP 403**
   - Respuesta: `{"detalle": "No tiene acceso a este reporte", "codigo": 403}`
5. `GET /reportes/2/historial` como *mantenimiento (Técnico Uno)* → **HTTP 403**
   - Respuesta: `{"detalle": "No tiene acceso a este reporte", "codigo": 403}`
6. `GET /reportes` como *coordinación* → **HTTP 200**
   - Respuesta: `[{"id": 2, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:39.313368", "creador": {"id": 5, "nombre": "Administrativo Prueba"}, "grupo": "pendiente"}, {"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombr…`

## PF-18 - Fotografías: formato y contenido válidos; archivos no permitidos se rechazan

- **Requisito:** RF-04, RNF-02  |  **Criterio:** CA-01
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada + reporte del docente.
- **Resultado esperado:** JPG válido HTTP 201; ejecutable y falso PNG HTTP 422; otro reportante HTTP 403; el reporte conserva 1 foto.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `POST /reportes` como *reportante (docente)* → **HTTP 201**
   - Entrada: `{"espacio_id": 1, "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "tipo_falla": "iluminacion"}`
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:39.449732", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`
2. `POST /reportes/1/fotos` como *reportante (docente)* → **HTTP 201**
   - Entrada: `"(archivo adjunto)"`
   - Respuesta: `{"id": 1, "nombre_original": "foto.jpg", "tipo_contenido": "image/jpeg", "tamano_bytes": 36, "subido_en": "2026-11-19T22:00:39.481674"}`
3. `POST /reportes/1/fotos` como *reportante (docente)* → **HTTP 422**
   - Entrada: `"(archivo adjunto)"`
   - Respuesta: `{"detalle": "Formato no permitido: use JPG, PNG o WEBP", "codigo": 422}`
4. `POST /reportes/1/fotos` como *reportante (docente)* → **HTTP 422**
   - Entrada: `"(archivo adjunto)"`
   - Respuesta: `{"detalle": "El contenido del archivo no corresponde a una imagen válida", "codigo": 422}`
5. `POST /reportes/1/fotos` como *reportante (administrativo)* → **HTTP 403**
   - Entrada: `"(archivo adjunto)"`
   - Respuesta: `{"detalle": "No tiene acceso a este reporte", "codigo": 403}`
6. `GET /reportes/1` como *reportante (docente)* → **HTTP 200**
   - Respuesta: `{"id": 1, "espacio": {"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, "tipo_falla": "iluminacion", "descripcion": "La lámpara del salón no enciende", "fecha_inicio_falla": "2026-11-18", "estado": "reportado", "prioridad": null, "duplicado_de_id": null, "creado_en": "2026-11-19T22:00:39.449732", "creador": {"id": 4, "nombre": "Docente Prueba", "correo": "doc@prueba.test", "telefono": "3001112233", "cargo": "docente"}, "urgencia_reportada": null, "requiere_verificacion": false, "motivo_rechazo": null,…`

## PF-19 - Coordinación mantiene el catálogo de espacios; los reportantes solo lo consultan

- **Requisito:** RF-02  |  **Criterio:** CA-01
- **Condiciones iniciales:** BD vacía de reportes con edificio «Bloque A», 3 espacios y una cuenta por perfil (coordinación, 2 técnicos, docente, administrativo), todas con sesión iniciada.
- **Resultado esperado:** Un reportante lista espacios (200) pero crear da 403; coordinación crea (201) y un nombre repetido en el mismo edificio da 409.
- **Resultado obtenido:** APROBADA

Pasos ejecutados contra la API:

1. `GET /espacios` como *reportante (docente)* → **HTTP 200**
   - Respuesta: `[{"id": 1, "nombre": "Aula 101", "tipo": "aula", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, {"id": 3, "nombre": "Cafetería", "tipo": "zona_comun", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}, {"id": 2, "nombre": "Laboratorio 1", "tipo": "laboratorio", "piso": null, "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}]`
2. `GET /edificios` como *reportante (docente)* → **HTTP 200**
   - Respuesta: `[{"id": 1, "nombre": "Bloque A", "descripcion": null}]`
3. `POST /espacios` como *reportante (docente)* → **HTTP 403**
   - Entrada: `{"edificio_id": 1, "nombre": "Sala de profesores", "tipo": "oficina", "piso": "2"}`
   - Respuesta: `{"detalle": "Su perfil no tiene permiso para realizar esta acción", "codigo": 403}`
4. `POST /espacios` como *coordinación* → **HTTP 201**
   - Entrada: `{"edificio_id": 1, "nombre": "Sala de profesores", "tipo": "oficina", "piso": "2"}`
   - Respuesta: `{"id": 4, "nombre": "Sala de profesores", "tipo": "oficina", "piso": "2", "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}`
5. `POST /espacios` como *coordinación* → **HTTP 409**
   - Entrada: `{"edificio_id": 1, "nombre": "Sala de profesores", "tipo": "oficina", "piso": "2"}`
   - Respuesta: `{"detalle": "Ya existe un espacio con ese nombre en el edificio", "codigo": 409}`
6. `POST /espacios` como *coordinación* → **HTTP 404**
   - Entrada: `{"edificio_id": 999, "nombre": "Sala de profesores", "tipo": "oficina", "piso": "2"}`
   - Respuesta: `{"detalle": "Edificio no encontrado", "codigo": 404}`
7. `PATCH /espacios/4` como *coordinación* → **HTTP 200**
   - Entrada: `{"nombre": "Sala docentes"}`
   - Respuesta: `{"id": 4, "nombre": "Sala docentes", "tipo": "oficina", "piso": "2", "activo": true, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}`
8. `PATCH /espacios/4` como *coordinación* → **HTTP 200**
   - Entrada: `{"activo": false}`
   - Respuesta: `{"id": 4, "nombre": "Sala docentes", "tipo": "oficina", "piso": "2", "activo": false, "edificio": {"id": 1, "nombre": "Bloque A", "descripcion": null}}`
9. `POST /reportes` como *reportante (docente)* → **HTTP 422**
   - Entrada: `{"espacio_id": 4, "descripcion": "Falla en espacio inactivo", "fecha_inicio_falla": "2026-11-18"}`
   - Respuesta: `{"detalle": "El espacio indicado no existe o está inactivo", "codigo": 422}`
