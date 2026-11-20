# Gestión de mantenimiento de instalaciones (Proyecto final PF-05)

Aplicación web para reportar y atender fallas de infraestructura de una sede: interfaz, API REST (FastAPI)
y base de datos relacional.

> **Estado:** backend y frontend completos. Backend probado con 19 pruebas de API; flujo completo verificado desde la interfaz.

---

## 1. Información general

| | |
|---|---|
| **Proyecto** | Gestión de mantenimiento de instalaciones (PF-05) |
| **Problema** | Las fallas se reportan de manera informal y no hay trazabilidad de evaluación, asignación, intervención y cierre |
| **Curso** | Aplicaciones y Servicios Web - Tecnología en Desarrollo de Software |
| **Docente / cliente** | Juan Carlos Morales Guerra |
| **Fecha** | Noviembre de 2026 |
| **Repositorio** | [https://github.com/Alexiss039/instalaciones](https://github.com/Alexiss039/instalaciones) |

**Integrantes y aportes**

| Integrante | Aporte |
|---|---|
| Brayan Espinosa | Backend: modelo de datos, API REST, reglas de negocio, pruebas de API, evidencias y documentación técnica (commits con `alexisbrayan0444@gmail.com`) |
| Emanuel Ortiz | Frontend: interfaces por perfil, validaciones en el navegador e integración con la API (commits con `emanuel-2005@outlook.es`) |

## 2. Descripción del sistema

**Actores:** reportante (docentes y administrativos), personal de mantenimiento y coordinación.

**Alcance aprobado:** registro de fallas con fotografía, evaluación, gestión de duplicados, asignación de
responsables, registro de intervenciones, cierre con verificación y consulta del dashboard.
**Fuera de alcance:** repuestos, compras, costos, sensores IoT, contratos, SMS/WhatsApp e integraciones.

**Solución:** cada reporte recorre los estados `reportado → evaluado → asignado → en_atencion → cerrado`
(con `rechazado`, `duplicado` y `en_verificacion` como salidas o pasos adicionales). Cada perfil solo ve y
modifica lo que le corresponde. Detalle en [`docs/requisitos.md`](docs/requisitos.md).

## 3. Requisitos y alcance

- **Método:** cuestionario de 16 preguntas respondido por el docente (cliente) el 18/11/2026. Las preguntas y
  las respuestas textuales están en [`evidencias/entrevista/`](evidencias/entrevista/); el registro completo
  con las decisiones de diseño, en [`docs/requisitos.md`](docs/requisitos.md).
- **Requisitos:** 12 funcionales (RF-01 a RF-12), 6 no funcionales y 11 reglas de negocio.
- **Criterios de aceptación:** CA-01 a CA-06 de la guía, trazados en [`docs/trazabilidad.md`](docs/trazabilidad.md).
- **Supuestos por confirmar** con el cliente: listados al final de `docs/requisitos.md`.

## 4. Arquitectura, diseño de la API y modelo de datos

```
Frontend (HTML/CSS/JS)  ──HTTP+JSON/JWT──►  API REST FastAPI  ──SQLAlchemy──►  SQLite
```

Modelo de datos (9 tablas): `usuarios`, `edificios`, `espacios`, `reportes`, `fotos`, `historial_estados`,
`valoraciones_tecnicas`, `asignaciones`, `intervenciones`. El diagrama, los estados, los permisos y la
justificación tecnológica están en [`docs/diseno.md`](docs/diseno.md).

**Interfaz:** aplicación de una página (HTML, CSS y JavaScript sin dependencias) servida por la propia API, con un
menú distinto por perfil: el reportante registra y consulta sus fallas (con fotos); mantenimiento ve sus trabajos,
registra intervenciones y finaliza; coordinación evalúa, asigna, verifica, administra espacios y usuarios y
consulta el dashboard. Es responsive, siempre en tema claro, y usa un diseño de tarjetas de doble bisel con
navegación flotante (detalle en [`docs/diseno.md`](docs/diseno.md)).. Las capturas están en
[`evidencias/capturas/`](evidencias/capturas/).

## 5. Preparación del entorno

**Requisitos:** Python 3.11 o superior y Git.

```powershell
git clone https://github.com/Alexiss039/instalaciones.git
cd instalaciones
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

En Linux/macOS: `source venv/bin/activate`.

**Variables de entorno (opcional).** Copie `.env.example` como `backend/.env` y ajuste los valores. Sin
`SECRET_KEY` se genera una clave aleatoria al arrancar (las sesiones se cierran al reiniciar el servidor).
`ZONA_HORARIA` (por defecto `America/Bogota`) define qué día es «hoy» y los límites de los filtros por fecha;
las marcas de tiempo se guardan en UTC, así que el resultado no depende de la zona del servidor.

**Base de datos y datos de prueba.** La base SQLite se crea sola al iniciar. Para cargar edificios, espacios
y una cuenta por perfil (datos ficticios):

```powershell
cd backend
python -m app.seed
```

| Perfil | Correo | Contraseña |
|---|---|---|
| Coordinación | coordinacion@gmail.com | Demo1234 |
| Mantenimiento (eléctrico) | tecnico.electrico@gmail.com | Demo1234 |
| Mantenimiento (general) | tecnico.general@gmail.com | Demo1234 |
| Reportante (docente) | docente@gmail.com | Demo1234 |
| Reportante (administrativo) | administrativo@gmail.com | Demo1234 |

**Ejecutar** (desde `backend/`):

```powershell
uvicorn app.main:app --reload --port 8000
```

- API y documentación interactiva: <http://localhost:8000/docs>
- Interfaz web: <http://localhost:8000/> (el frontend de la carpeta `frontend/` lo sirve la misma aplicación; no requiere Node ni compilación).
- Con la base recién sembrada, entre con cualquiera de las cuentas de la tabla anterior.

**Ejecutar las pruebas** (desde `backend/`):

```powershell
pytest
```

## 6. Servicios web implementados

Todos los endpoints (salvo `/auth/registro`, `/auth/login` y `/salud`) requieren `Authorization: Bearer <token>`.

| Método | Ruta | Descripción | Perfil | Req. |
|---|---|---|---|---|
| POST | `/auth/registro` | Registro de un docente o administrativo | público | RF-01 |
| POST | `/auth/login` | Inicio de sesión (formulario `username` = correo, `password`) | público | RF-01 |
| GET | `/auth/yo` | Datos del usuario autenticado | todos | RF-01 |
| POST | `/usuarios` | Crear una cuenta de cualquier perfil | coordinación | RF-01 |
| GET | `/usuarios`, `/usuarios/{id}` | Consultar cuentas | coordinación | RF-01 |
| PATCH | `/usuarios/{id}` | Actualizar datos, disponibilidad o activar/desactivar | coordinación | RF-01, RF-09 |
| GET | `/tecnicos` | Técnicos con experiencia, disponibilidad y carga | coordinación | RF-09 |
| GET | `/edificios`, `/espacios`, `/espacios/{id}` | Consultar el catálogo | todos | RF-02 |
| POST | `/edificios`, `/espacios` | Crear edificio o espacio | coordinación | RF-02 |
| PATCH | `/espacios/{id}` | Editar o desactivar un espacio | coordinación | RF-02 |
| POST | `/reportes` | Registrar una falla | reportante | RF-03 |
| POST | `/reportes/{id}/fotos` | Adjuntar fotografía (multipart, campo `archivo`) | reportante | RF-04 |
| GET | `/reportes/{id}/fotos/{foto_id}` | Descargar fotografía | quien ve el reporte | RF-04 |
| GET | `/reportes` | Listar (filtros: `estado`, `grupo`, `espacio_id`, `tipo_falla`, `prioridad`, `tecnico_id`, `desde`, `hasta`, `limite`, `desplazamiento`) | todos, según perfil | RF-05 |
| GET | `/reportes/{id}` | Detalle con fotos, asignaciones, intervenciones e historial | según perfil | RF-05 |
| GET | `/reportes/{id}/historial` | Historial de estados | según perfil | RF-08 |
| GET | `/reportes/{id}/posibles-duplicados` | Abiertos del mismo espacio y tipo | coordinación | RF-07 |
| POST | `/reportes/{id}/valoraciones` | Pedir apoyo técnico a un técnico | coordinación | RF-06 |
| POST | `/reportes/{id}/valoraciones/{vid}/respuesta` | Entregar concepto técnico | mantenimiento | RF-06 |
| POST | `/reportes/{id}/evaluacion` | Aceptar (prioridad) / rechazar (motivo) / duplicado | coordinación | RF-06, RF-07 |
| POST | `/reportes/{id}/asignaciones` | Asignar o reasignar responsable / apoyo | coordinación | RF-09 |
| POST | `/reportes/{id}/asignaciones/{aid}/retiro` | Retirar personal de apoyo | coordinación | RF-09 |
| POST | `/reportes/{id}/intervenciones` | Registrar una intervención | mantenimiento asignado | RF-10 |
| GET | `/reportes/{id}/intervenciones` | Historial de intervenciones | según perfil | RF-10 |
| POST | `/reportes/{id}/finalizar` | Informar fin del trabajo con resultado | responsable / coordinación | RF-11 |
| POST | `/reportes/{id}/verificacion` | Aprobar o devolver el cierre | coordinación | RF-11 |
| GET | `/dashboard/resumen` | Dashboard (`desde`, `hasta`) | coordinación | RF-12 |
| GET | `/salud` | Verificación de funcionamiento | público | - |

**Ejemplo - registrar una falla**

```http
POST /reportes
{"espacio_id": 1, "descripcion": "El proyector del aula no enciende",
 "fecha_inicio_falla": "2026-11-18", "tipo_falla": "electrica", "urgencia_reportada": "alta"}
```

```json
HTTP 201
{"id": 1, "estado": "reportado", "grupo": "pendiente", "espacio": {"nombre": "Aula 101", "...": "..."}, "...": "..."}
```

**Ejemplo - evaluar**

```http
POST /reportes/1/evaluacion
{"decision": "aceptar", "prioridad": "alta"}
```

**Validaciones y errores:** todos los errores usan `{"detalle": "...", "codigo": N}`.

| Código | Cuándo |
|---|---|
| 401 | Sin sesión, token inválido o credenciales incorrectas |
| 403 | El perfil no tiene permiso o el reporte no es suyo |
| 404 | Recurso inexistente |
| 409 | Transición de estado no permitida, duplicados, técnico no disponible |
| 422 | Datos inválidos o regla de negocio incumplida (con la lista `errores` por campo) |
| 500 | Error inesperado (sin detalles internos; queda en el log del servidor) |

## 7. Resultados de las pruebas

19 pruebas de API automatizadas con pytest (la guía exige un mínimo de 12; PF-01 a PF-12 son las pedidas y
PF-13 a PF-19 son adicionales). **Resultado: 19 aprobadas, 0 fallidas.**

| ID | Prueba | Req. | HTTP |
|---|---|---|---|
| PF-01 | Registrar reporte válido y comprobar que persiste | RF-03 | 201 / 200 |
| PF-02 | Datos faltantes o inválidos, sin crear registros | RF-03 | 422 |
| PF-03 | Listar reportes y consultar detalle | RF-05 | 200 |
| PF-04 | Reporte inexistente | RNF-02 | 404 |
| PF-05 | Evaluar: aceptar con prioridad / rechazar con motivo | RF-06 | 200 / 422 |
| PF-06 | Transición de estado no permitida | RF-08 | 409 |
| PF-07 | Asignar responsable; persistencia y visibilidad | RF-09 | 201 / 200 |
| PF-08 | Usuario no autorizado bloqueado sin cambios | RNF-01 | 401 / 403 |
| PF-09 | Intervención válida e inválidas | RF-10 | 201 / 403 / 422 |
| PF-10 | Cierre con resultado e historial | RF-11 | 200 / 409 |
| PF-11 | Dashboard con conteos y filtros por fecha | RF-12 | 200 / 422 |
| PF-12 | Flujo completo reporte → cierre | RF-03 a RF-12 | 2xx |
| PF-13 a PF-19 | Duplicados, autenticación, verificación, reasignación, visibilidad, fotos, espacios | ver trazabilidad | varios |

**Reproducir y regenerar evidencias** (desde `backend/`):

```powershell
pytest                    # ejecuta las pruebas
$env:EVIDENCIAS = "1"; pytest   # además escribe evidencias/pruebas_api.md y resultados_pruebas.json
```

Las evidencias (petición, respuesta y código HTTP de cada paso) están en
[`evidencias/pruebas_api.md`](evidencias/pruebas_api.md). La matriz completa está en
[`docs/trazabilidad.md`](docs/trazabilidad.md).

**Flujo completo desde la interfaz (PF-12):** guion, resultados observados y capturas en
[`evidencias/flujo_interfaz.md`](evidencias/flujo_interfaz.md): reporte con foto → evaluación → asignación →
intervención → finalización → verificación → cierre → dashboard, pasando por interfaz, API y base de datos.

## 8. Control de versiones

- **Repositorio:** [https://github.com/Alexiss039/instalaciones](https://github.com/Alexiss039/instalaciones).
- **Flujo:** rama `main` protegida por pull requests; ramas `feature/...` por funcionalidad; commits
  descriptivos.
- **Backend:** commits y PR de Brayan Espinosa. **Frontend:** commits y PR de Emanuel Ortiz, revisados de
  forma cruzada.

| PR | Contenido | Autor | Revisor |
|---|---|---|---|
| [#1](https://github.com/Alexiss039/instalaciones/pull/1) | Backend: API, modelo de datos, pruebas, evidencias y documentación | Brayan Espinosa | Emanuel Ortiz |
| [#2](https://github.com/Alexiss039/instalaciones/pull/2) | Frontend: interfaz web por perfil | Emanuel Ortiz | Brayan Espinosa |
| [#3](https://github.com/Alexiss039/instalaciones/pull/3) | Backend: servicio y criterio «dashboard», usuarios de demostración simples, evidencias y capturas | Brayan Espinosa | Emanuel Ortiz |
| [#4](https://github.com/Alexiss039/instalaciones/pull/4) | Documentación: enlace del repositorio, tabla de PR, aportes por integrante, aprobación del docente y diagramas | Emanuel Ortiz | Brayan Espinosa |

## 9. Conclusiones y limitaciones

- El backend cubre CA-01 a CA-06 con control de acceso por perfil, validaciones, historial y 19 pruebas.
- **Limitaciones:** SQLite (suficiente para una sede; cambiar `DATABASE_URL` para otro motor); las fotos se
  guardan en disco local; no hay recuperación de contraseña ni notificaciones (fuera del alcance acordado).
- **Interfaz:** probada manualmente en el navegador (flujo completo, validaciones del servidor y vista móvil de 375 px);
  no tiene pruebas automatizadas, solo el guion documentado.
- **Evidencias de la interfaz:** 8 capturas del flujo completo en `evidencias/capturas/` (guion en
  `evidencias/flujo_interfaz.md`).
- **Pendiente de aprobación:** el cliente respondió las 16 preguntas, pero todavía no ha confirmado por
  escrito el alcance ni los cuatro supuestos de la sección 7 de [`docs/requisitos.md`](docs/requisitos.md),
  que son decisiones tomadas por el equipo a partir de sus respuestas.
