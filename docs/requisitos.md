# Requisitos - Gestión de mantenimiento de instalaciones (PF-05)

**Equipo:** Brayan Espinosa, Emanuel Ortiz  
**Cliente:** Juan Carlos Morales Guerra (docente, en representación de la organización)  
**Método:** cuestionario escrito de 16 preguntas enviado el 11/11/2026 y respondido por el cliente el 18/11/2026.

> **Estado de aprobación:** el docente (cliente) aprobó las respuestas de las 16 preguntas, el alcance y los
> supuestos marcados como **[Supuesto]** (sección 7).

## 1. Alcance

Aplicación web (interfaz, API REST y base de datos) para reportar y atender fallas de infraestructura en
una sede con varios edificios: aulas, oficinas, laboratorios y zonas comunes.

**Actores**

| Actor | Quién es | Qué hace |
|---|---|---|
| Reportante | Docentes y personal administrativo, cada uno con cuenta y datos de contacto | Reporta fallas y consulta sus propios casos |
| Mantenimiento | Técnicos | Valoran técnicamente si coordinación lo pide, registran intervenciones en lo asignado y finalizan |
| Coordinación | Responsables de la gestión | Evalúan, asignan y reasignan, verifican cierres y consultan todo |

**Fuera de alcance (confirmado):** repuestos, compras, costos contables, mantenimiento predictivo, sensores
IoT, contratos, SMS/WhatsApp e integración con plataformas institucionales.

## 2. Registro de la entrevista

| N.° | Respuesta del cliente (resumen fiel) | Decisión de diseño |
|---|---|---|
| 1 | Aulas, oficinas, laboratorios y zonas comunes; una sola sede con varios edificios | Tablas `edificios` y `espacios`; tipo de espacio como catálogo |
| 2 | Los espacios ya están identificados, pero deben poder actualizarse cuando cambien | Catálogo precargado; coordinación crea, edita y desactiva desde la app |
| 3 | Se necesita saber quién reporta, dónde, qué pasa y desde cuándo; la foto ayuda | Campos: reportante, espacio, descripción, fecha de inicio de la falla, tipo, urgencia y fotos |
| 4 | Reportan docentes y administrativos, identificados para poder contactarlos | Cuenta obligatoria con nombre, correo, teléfono y cargo |
| 5 | Varios reportan lo mismo: evitar trabajo duplicado, conservar quién reportó | Coordinación marca el duplicado y lo vincula al original; todos los reportantes se conservan |
| 6 | Coordinación revisa primero y pide apoyo técnico a mantenimiento si hace falta | Coordinación evalúa; puede solicitar una valoración técnica a un técnico |
| 7 | Se revisa si corresponde a las instalaciones, si la información alcanza y la urgencia | La evaluación registra esos tres juicios (aceptar con prioridad, rechazar con motivo o duplicado) |
| 8 | Distinguir pendientes, en atención y finalizados; saber cuáles no se solucionaron y por qué | Estados agrupados en 3 grupos; resultado de cierre con motivo |
| 9 | Coordinación asigna responsables y puede cambiarlos | Solo coordinación asigna y reasigna; el personal no se autoasigna |
| 10 | Se considera tipo de falla, experiencia, disponibilidad y trabajos pendientes | El sistema muestra esos criterios al asignar; la decisión es de coordinación **[Supuesto]**, salvo que no se puede asignar a quien está no disponible |
| 11 | Fecha, quién, actividades, tiempo empleado y resultado | Entidad `intervenciones` con esos campos |
| 12 | Cada técnico registra su trabajo; si participan varios, identificar cada intervención | Varios técnicos asignados (responsable + apoyo); cada intervención guarda a su autor |
| 13 | Para terminar se necesita el trabajo realizado y el resultado; algunos casos requieren verificación de coordinación | Cierre exige ≥ 1 intervención, descripción de la solución y resultado; verificación según prioridad o resultado **[Supuesto]** |
| 14 | El responsable informa cuando termina y coordinación puede verificar; algunas fallas requieren apoyo externo o no se solucionan de inmediato | Resultados: resuelto, no reproducible, requiere tercero, no solucionable (con motivo) |
| 15 | El reportante ve lo suyo, el técnico lo asignado, coordinación todo; cada persona con su cuenta | Autenticación con JWT y permisos por perfil; las cuentas de técnicos y coordinación las crea coordinación **[Supuesto]**; los reportantes pueden auto-registrarse **[Supuesto]** |
| 16 | Pendientes, en atención y finalizados; fallas frecuentes, espacios afectados, responsables; por fechas | Servicio del dashboard con filtro `desde`/`hasta` |

## 3. Requisitos funcionales (RF)

| ID | Requisito | Prioridad |
|---|---|---|
| RF-01 | El sistema permite registrar cuentas de reportante, iniciar sesión y mantener cuentas por perfil (reportante, mantenimiento, coordinación) | Alta |
| RF-02 | Los usuarios autenticados consultan edificios y espacios; coordinación los crea, edita y desactiva | Alta |
| RF-03 | Un reportante registra una falla indicando espacio, descripción, fecha de inicio, tipo de falla y urgencia (opcional) | Alta |
| RF-04 | El reportante adjunta fotografías (JPG, PNG, WEBP) a su reporte | Media |
| RF-05 | Cada perfil consulta solo lo que le corresponde: reportante sus reportes, técnico los asignados o a valorar, coordinación todos; con filtros por estado, grupo, espacio, tipo y fechas | Alta |
| RF-06 | Coordinación evalúa un reporte: acepta con prioridad, rechaza con motivo o lo marca como duplicado; puede pedir antes una valoración técnica a un técnico | Alta |
| RF-07 | Los reportes repetidos se vinculan al original y se conservan todos los reportantes | Alta |
| RF-08 | El reporte recorre estados controlados (ver `diseno.md`); las transiciones inválidas se rechazan y cada cambio queda en el historial | Alta |
| RF-09 | Coordinación asigna un responsable y personal de apoyo, y puede reasignar (con motivo); ve experiencia, disponibilidad y carga de cada técnico | Alta |
| RF-10 | El técnico asignado registra intervenciones: fecha, actividades, tiempo empleado y resultado; cada una queda a su nombre | Alta |
| RF-11 | El responsable finaliza el reporte con resultado y descripción de la solución; coordinación verifica cuando corresponde o cierra directamente. Los casos no resueltos guardan el motivo | Alta |
| RF-12 | Coordinación consulta el dashboard (la «información consolidada» de la guía): reportes por grupo y estado, fallas más frecuentes, espacios afectados, responsables y resultados, filtrado por fechas | Alta |

## 4. Requisitos no funcionales (RNF)

| ID | Requisito |
|---|---|
| RNF-01 | Control de acceso por perfil en el servidor; un usuario no puede ver ni modificar lo que no le corresponde |
| RNF-02 | Validación de datos en el servidor y errores controlados (códigos HTTP 400, 401, 403, 404, 409, 422) sin exponer información interna |
| RNF-03 | Contraseñas con hash (PBKDF2), sesión con JWT y sin secretos en el repositorio |
| RNF-04 | El proyecto se instala y ejecuta siguiendo únicamente el README |
| RNF-05 | La API queda documentada automáticamente (OpenAPI / Swagger en `/docs`) |
| RNF-06 | Trazabilidad: historial de estados con usuario, fecha y comentario; las asignaciones retiradas se conservan |

## 5. Reglas de negocio (RN)

| ID | Regla |
|---|---|
| RN-01 | Solo los perfiles reportantes crean reportes; solo coordinación evalúa, asigna, reasigna y verifica |
| RN-02 | Un reporte solo se evalúa estando en `reportado`. Aceptar exige prioridad; rechazar exige motivo; duplicado exige el reporte original |
| RN-03 | No se puede aceptar una falla que no corresponde a las instalaciones ni con información insuficiente |
| RN-04 | Prioridad alta o crítica implica verificación de coordinación al cerrar (coordinación puede cambiarlo al evaluar) |
| RN-05 | Un reporte duplicado no se atiende; su reportante puede seguir el avance del reporte original |
| RN-06 | No se asigna a un técnico no disponible, inactivo o ya asignado al mismo reporte; cambiar de responsable exige motivo |
| RN-07 | Solo el personal asignado registra intervenciones; la primera lleva el reporte a `en_atencion` |
| RN-08 | No se puede cerrar un reporte sin al menos una intervención |
| RN-09 | Si el resultado no es «resuelto» se exige el motivo y coordinación debe verificar el cierre |
| RN-10 | Los reportes cerrados, rechazados y duplicados no cambian de estado |
| RN-11 | Las fechas de falla e intervención no pueden ser futuras; la intervención no puede ser anterior al inicio de la falla |

## 6. Historias de usuario y criterios de aceptación

| Historia | Criterio verificable | CA |
|---|---|---|
| Como docente quiero reportar una falla en un espacio para que sea atendida | Con datos válidos se crea el reporte (HTTP 201) y se puede consultar; con datos inválidos HTTP 422 sin crear registros | CA-01 |
| Como coordinador quiero evaluar y priorizar los reportes | La decisión y el estado quedan registrados y visibles; una evaluación repetida da HTTP 409 | CA-02 |
| Como coordinador quiero asignar responsables según su perfil | La asignación persiste y es visible para coordinación y para el técnico asignado | CA-03 |
| Como técnico quiero registrar lo que hice en cada visita | La intervención queda ligada al reporte y a su autor, con historial | CA-04 |
| Como técnico quiero informar que terminé y como coordinador verificarlo | El cierre guarda resultado y solución; consultable por quien corresponda | CA-05 |
| Como coordinador quiero ver pendientes, en atención y finalizados por fechas | Los conteos del dashboard coinciden con los reportes almacenados | CA-06 |

## 7. Supuestos (aprobados por el cliente)

1. Las cuentas de técnicos y coordinación las crea coordinación; los docentes/administrativos pueden auto-registrarse.
2. Un reporte de prioridad alta o crítica, o con resultado distinto de «resuelto», pasa por verificación de coordinación.
3. Se permiten varios técnicos por reporte (un responsable y personal de apoyo).
4. La experiencia y especialidad del técnico se muestran como apoyo a la decisión; no bloquean la asignación.
