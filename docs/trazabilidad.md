# Matriz de trazabilidad

Relaciona cada criterio de aceptación (CA) con su requisito, la implementación, el pull request y la prueba
que lo verifica. Las pruebas están en `backend/tests/test_api.py`; su evidencia, en
[`evidencias/pruebas_api.md`](../evidencias/pruebas_api.md).

> La columna **PR** enlaza los pull requests de GitHub (backend: Brayan Espinosa; frontend: Emanuel Ortiz).

| CA | Requisito | Implementación (backend) | Interfaz (frontend) | PR | Pruebas |
|---|---|---|---|---|---|
| **CA-01** Registrar y consultar una falla vinculada a un espacio | RF-02, RF-03, RF-04, RF-05 | `POST /reportes`, `GET /reportes`, `GET /reportes/{id}`, `POST /reportes/{id}/fotos`, `GET /espacios` · `routers/reportes.py`, `routers/espacios.py` | `vistas/nuevo.js` (formulario con fotos), `vistas/lista.js`, `vistas/detalle.js` | [#1](https://github.com/Alexiss039/instalaciones/pull/1), [#3](https://github.com/Alexiss039/instalaciones/pull/3) (backend) / [#2](https://github.com/Alexiss039/instalaciones/pull/2) (frontend) | PF-01, PF-02, PF-03, PF-04, PF-17, PF-18, PF-19 |
| **CA-02** Evaluar y gestionar; la decisión queda registrada y visible | RF-06, RF-07, RF-08 | `POST /reportes/{id}/evaluacion`, `POST /reportes/{id}/valoraciones`, `GET /reportes/{id}/historial` · `servicios.py` (transiciones) | `vistas/detalle.js` (`formEvaluacion`, `formValoracion`) | [#1](https://github.com/Alexiss039/instalaciones/pull/1), [#3](https://github.com/Alexiss039/instalaciones/pull/3) (backend) / [#2](https://github.com/Alexiss039/instalaciones/pull/2) (frontend) | PF-05, PF-06, PF-08, PF-13 |
| **CA-03** Asignar responsable; persiste y es visible | RF-09 | `POST /reportes/{id}/asignaciones`, `GET /tecnicos` · `routers/reportes.py`, `routers/usuarios.py` | `vistas/detalle.js` (`formAsignar`, retiro de apoyo) | [#1](https://github.com/Alexiss039/instalaciones/pull/1), [#3](https://github.com/Alexiss039/instalaciones/pull/3) (backend) / [#2](https://github.com/Alexiss039/instalaciones/pull/2) (frontend) | PF-07, PF-08, PF-16, PF-17 |
| **CA-04** Registrar intervenciones con historial | RF-10 | `POST /reportes/{id}/intervenciones`, `GET /reportes/{id}/intervenciones` | `vistas/detalle.js` (`formIntervencion`, lista de intervenciones) | [#1](https://github.com/Alexiss039/instalaciones/pull/1), [#3](https://github.com/Alexiss039/instalaciones/pull/3) (backend) / [#2](https://github.com/Alexiss039/instalaciones/pull/2) (frontend) | PF-09, PF-12 |
| **CA-05** Cerrar el servicio y conservar el resultado | RF-11, RF-08 | `POST /reportes/{id}/finalizar`, `POST /reportes/{id}/verificacion` | `vistas/detalle.js` (`formFinalizar`, `formVerificacion`, bloque de cierre) | [#1](https://github.com/Alexiss039/instalaciones/pull/1), [#3](https://github.com/Alexiss039/instalaciones/pull/3) (backend) / [#2](https://github.com/Alexiss039/instalaciones/pull/2) (frontend) | PF-10, PF-12, PF-15 |
| **CA-06** Dashboard (información consolidada de la guía) agrupado y filtrado | RF-12 | `GET /dashboard/resumen`, filtros de `GET /reportes` · `routers/dashboard.py` | `vistas/dashboard.js`, filtros de `vistas/lista.js` | [#1](https://github.com/Alexiss039/instalaciones/pull/1), [#3](https://github.com/Alexiss039/instalaciones/pull/3) (backend) / [#2](https://github.com/Alexiss039/instalaciones/pull/2) (frontend) | PF-11, PF-12 |

## Requisitos transversales

| Requisito | Dónde se implementa | Pruebas |
|---|---|---|
| RF-01 Cuentas y autenticación | `routers/auth.py`, `routers/usuarios.py`, `seguridad.py` | PF-14, PF-16 |
| RNF-01 Control de acceso por perfil | `dependencias.requiere_roles`, `servicios.puede_ver` | PF-08, PF-17 |
| RNF-02 Validación y errores controlados | `schemas.py`, `errores.py` | PF-02, PF-04, PF-18 |
| RNF-03 Seguridad de credenciales | `seguridad.py`, `.env.example`, `.gitignore` | PF-14 |
| RNF-04 Instalación reproducible | `README.md`, `backend/requirements.txt`, `app/seed.py` | Verificado siguiendo el README |
| RNF-05 Documentación de la API | OpenAPI en `/docs` | - |
| RNF-06 Historial y auditoría | tabla `historial_estados`, asignaciones conservadas | PF-10, PF-16 |

## Pruebas funcionales

| ID | Prueba | Requisito | CA | HTTP esperado |
|---|---|---|---|---|
| PF-01 | Registrar reporte válido y comprobar que persiste | RF-03, RF-05 | CA-01 | 201, 200 |
| PF-02 | Rechazar datos obligatorios faltantes o inválidos | RF-03, RNF-02 | CA-01 | 422 |
| PF-03 | Listar reportes y consultar un detalle | RF-05 | CA-01 | 200 |
| PF-04 | Reporte inexistente | RNF-02 | CA-01 | 404 |
| PF-05 | Evaluar: aceptar con prioridad / rechazar con motivo | RF-06 | CA-02 | 200, 422 |
| PF-06 | Transición de estado no permitida | RF-08 | CA-02 | 409 |
| PF-07 | Asignar responsable; persistencia y visibilidad | RF-09, RF-05 | CA-03 | 201, 200 |
| PF-08 | Usuario no autorizado bloqueado sin cambios | RNF-01 | CA-02, CA-03 | 401, 403 |
| PF-09 | Registrar intervención válida e inválidas | RF-10 | CA-04 | 201, 403, 422 |
| PF-10 | Cerrar reporte y consultar resultado con historial | RF-11, RF-08 | CA-05 | 200, 409 |
| PF-11 | Dashboard con conteos y filtros | RF-12 | CA-06 | 200, 422 |
| PF-12 | Flujo completo reporte → cierre (API) | RF-03 a RF-12 | CA-01 a CA-06 | 2xx |
| PF-13 | Duplicados y conservación de reportantes | RF-07 | CA-02 | 200, 422 |
| PF-14 | Registro, login y credenciales inválidas | RF-01, RNF-03 | CA-01 | 201, 401, 409, 422 |
| PF-15 | Verificación de cierre y resultados no resueltos | RF-11 | CA-05 | 200, 403, 422 |
| PF-16 | Reasignación, motivo y disponibilidad | RF-09 | CA-03 | 201, 409, 422 |
| PF-17 | Visibilidad por perfil | RF-05, RNF-01 | CA-01, CA-03 | 200, 403 |
| PF-18 | Fotografías: formatos y contenido | RF-04, RNF-02 | CA-01 | 201, 403, 422 |
| PF-19 | Catálogo de espacios | RF-02 | CA-01 | 201, 403, 404, 409, 422 |

> PF-12 se ejecuta a nivel de API (automatizado) y también desde la interfaz, siguiendo el guion de
> [`evidencias/flujo_interfaz.md`](../evidencias/flujo_interfaz.md), que cubre el flujo interfaz → API → base de datos.
> Las rutas `vistas/...` son de `frontend/js/`.
