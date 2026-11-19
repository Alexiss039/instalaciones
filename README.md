# Gestión de mantenimiento de instalaciones (Proyecto final PF-05)

Aplicación web para reportar y atender fallas de infraestructura de una sede: interfaz, API REST (FastAPI)
y base de datos relacional.

> **Estado:** backend completo y probado. El frontend está pendiente (carpeta `frontend/`).

---

## 1. Información general

| | |
|---|---|
| **Proyecto** | Gestión de mantenimiento de instalaciones (PF-05) |
| **Problema** | Las fallas se reportan de manera informal y no hay trazabilidad de evaluación, asignación, intervención y cierre |
| **Curso** | Aplicaciones y Servicios Web - Tecnología en Desarrollo de Software |
| **Docente / cliente** | Juan Carlos Morales Guerra |
| **Fecha** | Noviembre de 2026 |
| **Repositorio** | _Pendiente: agregar el enlace de GitHub_ |

**Integrantes y aportes**

| Integrante | Aporte |
|---|---|
| Brayan Espinoza | Backend: modelo de datos, API REST, reglas de negocio, pruebas y documentación técnica |
| Emanuel Ortiz | Frontend: interfaces por perfil e integración con la API |

## 2. Descripción del sistema

**Actores:** reportante (docentes y administrativos), personal de mantenimiento y coordinación.

**Alcance aprobado:** registro de fallas con fotografía, evaluación, gestión de duplicados, asignación de
responsables, registro de intervenciones, cierre con verificación y consulta consolidada.
**Fuera de alcance:** repuestos, compras, costos, sensores IoT, contratos, SMS/WhatsApp e integraciones.

**Solución:** cada reporte recorre los estados `reportado → evaluado → asignado → en_atencion → cerrado`
(con `rechazado`, `duplicado` y `en_verificacion` como salidas o pasos adicionales). Cada perfil solo ve y
modifica lo que le corresponde. Detalle en [`docs/requisitos.md`](docs/requisitos.md).

## 3. Requisitos y alcance

- **Método:** cuestionario de 16 preguntas respondido por el docente (cliente) el 18/11/2026; el registro
  completo con las decisiones de diseño está en [`docs/requisitos.md`](docs/requisitos.md).
- **Requisitos:** 12 funcionales (RF-01 a RF-12), 6 no funcionales y 11 reglas de negocio.
- **Criterios de aceptación:** CA-01 a CA-06 de la guía, trazados en [`docs/trazabilidad.md`](docs/trazabilidad.md).
- **Supuestos por confirmar** con el cliente: listados al final de `docs/requisitos.md`.

## 4. Arquitectura, diseño de la API y modelo de datos

```
Frontend (HTML/CSS/JS)  ──HTTP+JSON/JWT──►  API REST FastAPI  ──SQLAlchemy──►  SQLite
```

Modelo de datos (10 tablas): `usuarios`, `edificios`, `espacios`, `reportes`, `fotos`, `historial_estados`,
`valoraciones_tecnicas`, `asignaciones`, `intervenciones`. El diagrama, los estados, los permisos y la
justificación tecnológica están en [`docs/diseno.md`](docs/diseno.md).

> Las capturas de la interfaz se agregan cuando el frontend esté implementado.

## 5. Preparación del entorno

**Requisitos:** Python 3.11 o superior y Git.

```powershell
git clone <URL-DEL-REPOSITORIO>
cd instalaciones
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

En Linux/macOS: `source venv/bin/activate`.

**Variables de entorno (opcional).** Copie `.env.example` como `backend/.env` y ajuste los valores. Sin
`SECRET_KEY` se genera una clave aleatoria al arrancar (las sesiones se cierran al reiniciar el servidor).

**Base de datos y datos de prueba.** La base SQLite se crea sola al iniciar. Para cargar edificios, espacios
y una cuenta por perfil (datos ficticios):

```powershell
cd backend
python -m app.seed
```

| Perfil | Correo | Contraseña |
|---|---|---|
| Coordinación | coordinacion@demo.test | Demo1234 |
| Mantenimiento (eléctrico) | tecnico.electrico@demo.test | Demo1234 |
| Mantenimiento (general) | tecnico.general@demo.test | Demo1234 |
| Reportante (docente) | docente@demo.test | Demo1234 |
| Reportante (administrativo) | administrativo@demo.test | Demo1234 |

**Ejecutar** (desde `backend/`):

```powershell
uvicorn app.main:app --reload --port 8000
```

- API y documentación interactiva: <http://localhost:8000/docs>
- Frontend: se sirve desde la misma aplicación en <http://localhost:8000/> cuando exista la carpeta `frontend/`.

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
| GET | `/consolidado/resumen` | Consolidado (`desde`, `hasta`) | coordinación | RF-12 |
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
| PF-11 | Consolidado con conteos y filtros por fecha | RF-12 | 200 / 422 |
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

> Pendiente con el frontend: evidencia del flujo completo interfaz → API → base de datos.

## 8. Control de versiones

- **Repositorio:** _pendiente de agregar_.
- **Flujo:** rama `main` protegida por pull requests; ramas `feature/...` por funcionalidad; commits
  descriptivos.
- **Backend:** commits y PR de Brayan Espinoza. **Frontend:** commits y PR de Emanuel Ortiz, revisados de
  forma cruzada.

| PR | Contenido | Autor | Revisor |
|---|---|---|---|
| _por completar_ | | | |

## 9. Conclusiones y limitaciones

- El backend cubre CA-01 a CA-06 con control de acceso por perfil, validaciones, historial y 19 pruebas.
- **Limitaciones:** SQLite (suficiente para una sede; cambiar `DATABASE_URL` para otro motor); las fotos se
  guardan en disco local; no hay recuperación de contraseña ni notificaciones (fuera del alcance acordado).
- **Pendiente:** frontend, capturas de interfaz, prueba del flujo completo desde la interfaz, enlaces de
  GitHub y confirmación de los supuestos de `docs/requisitos.md` con el cliente.
