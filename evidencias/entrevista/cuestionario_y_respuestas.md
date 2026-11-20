# Cuestionario de levantamiento de requisitos y respuestas del cliente

Proyecto: Gestión de mantenimiento de instalaciones (PF-05)
Cliente: Juan Carlos Morales Guerra, docente, en representación de la organización
Enviado el 11/11/2026 · respondido el 18/11/2026

Las respuestas se transcriben tal como las entregó el cliente. En cursiva, bajo cada pregunta, las
opciones que planteó el equipo al momento de preguntar.

## 1. Espacios y reporte

**1. ¿Qué espacios debe cubrir el sistema (aulas, oficinas, laboratorios, zonas comunes u otros)? ¿Se trata de una sola sede o de varias sedes o edificios?**

> La organización atiende fallas en aulas, oficinas, laboratorios y zonas comunes. Por ahora, se contempla una sola sede con varios edificios.

**2. ¿Cómo se manejarán los espacios dentro de la aplicación?**
*Opciones planteadas: un catálogo ya definido que solo se consulta; la coordinación los crea y edita desde la aplicación; el reportante escribe el espacio libremente.*

> La institución tiene identificados sus espacios, pero necesita mantener esa información actualizada cuando se presenten cambios.

**3. ¿Qué datos debe suministrar quien reporta una falla?**
*Planteamos espacio y descripción como obligatorios; tipo de falla, urgencia y fotografía como opcionales.*

> Se necesita conocer quién reporta la falla, dónde ocurre, qué está pasando y desde cuándo. Las fotografías pueden ayudar a identificar el problema.

**4. ¿Quién puede reportar una falla?**
*Opciones planteadas: cualquier usuario con cuenta, identificado; también personas sin cuenta.*

> Los reportes los realizan docentes y personal administrativo. Es necesario identificar a cada persona para poder contactarla.

**5. Sobre los reportes repetidos: ¿cómo se reconoce uno repetido y qué debe hacer el sistema cuando ocurra?**
*Opciones planteadas: avisar al reportante; que quien evalúa lo marque y lo vincule al original; bloquearlo si ya hay uno abierto; solo contar las repeticiones.*

> En ocasiones, varias personas reportan la misma falla. Se necesita evitar trabajos duplicados, pero conservar la información de quienes realizaron los reportes.

## 2. Evaluación y estados

**6. ¿Quién evalúa un reporte?**
*Opciones planteadas: la coordinación; el personal de mantenimiento; ambos.*

> La coordinación revisa inicialmente los reportes y solicita apoyo del personal de mantenimiento cuando requiere una valoración técnica.

**7. ¿Qué decisiones puede tomar quien evalúa?**
*Planteamos aceptar, rechazar con motivo, marcar como repetido y definir la prioridad.*

> Se revisa si la falla corresponde a las instalaciones, si la información es suficiente y qué tan urgente es atenderla.

**8. ¿Por qué estados debe pasar un reporte? ¿Qué cambios de estado no deben permitirse?**
*Planteamos Reportado, Evaluado, Asignado, En atención y Cerrado, con Rechazado como salida posterior a la evaluación.*

> La organización necesita distinguir los reportes pendientes, los que están siendo atendidos y los finalizados. También debe conocer cuáles no pudieron solucionarse y por qué.

## 3. Asignación

**9. ¿Quién asigna al responsable de un reporte?**
*Opciones planteadas: solo la coordinación; el personal también puede tomar un reporte por su cuenta.*

> La coordinación asigna los responsables y puede realizar cambios cuando sea necesario.

**10. Al asignar un responsable, ¿qué se tiene en cuenta para escogerlo?**
*Ejemplos planteados: especialidad, cantidad de reportes a cargo, disponibilidad y zona de trabajo.*

> Se considera el tipo de falla, la experiencia del personal, su disponibilidad y los trabajos que tiene pendientes.

## 4. Intervenciones y cierre

**11. ¿Qué datos debe tener una intervención?**
*Planteamos fecha, descripción de lo realizado, avance o resultado y quién la registró; tiempo empleado como posible adición.*

> Se necesita conocer la fecha de intervención, quién realizó el trabajo, qué actividades desarrolló, cuánto tiempo empleó y cuál fue el resultado.

**12. ¿Quién puede registrar intervenciones?**
*Opciones planteadas: solo el responsable asignado; cualquier integrante del personal de mantenimiento.*

> Normalmente, cada técnico registra el trabajo que realiza. Cuando participan varias personas, es importante identificar sus intervenciones.

**13. ¿Qué se necesita para cerrar un reporte?**
*Opciones planteadas: descripción de la solución; al menos una intervención; confirmación del reportante; aprobación de la coordinación.*

> Para dar por terminado un reporte, se necesita conocer qué trabajo se realizó y cuál fue el resultado. Algunos casos requieren verificación de coordinación.

**14. ¿Quién puede cerrar un reporte y qué resultados de cierre existen?**
*Planteamos resuelto, no reproducible, requiere un tercero y rechazado.*

> El responsable informa cuando termina el trabajo y coordinación puede verificarlo. Algunas fallas requieren apoyo externo o no pueden solucionarse inmediatamente.

## 5. Permisos y consulta consolidada

**15. ¿Qué debe ver cada actor? ¿Cómo inician sesión los usuarios?**
*Planteamos que el reportante vea solo sus reportes, mantenimiento los asignados y la coordinación todos.*

> Quien reporta debe consultar sus propios casos, el personal de mantenimiento sus trabajos asignados y coordinación todos los reportes. Cada persona debe contar con su propia cuenta de acceso.

**16. ¿Qué información consolidada necesita la coordinación?**
*Planteamos cantidad de reportes por estado, espacio, tipo de falla y responsable, con filtro por fechas.*

> La coordinación necesita consultar reportes pendientes, en atención y finalizados, las fallas más frecuentes, los espacios afectados y los responsables. También requiere consultar la información por fechas.

## Puntos que quedaron abiertos

Las respuestas no definen los siguientes detalles, resueltos por el equipo como supuestos en la sección 7
de [`../../docs/requisitos.md`](../../docs/requisitos.md) y pendientes de confirmación con el cliente:

1. Quién crea y edita los espacios, y quién crea las cuentas de usuario.
2. Cómo se detecta un reporte repetido: lo marca la coordinación o el sistema lo advierte.
3. Qué casos exigen verificación de la coordinación al cerrar.
4. Si un caso que requiere apoyo externo se cierra o queda abierto en espera.
5. Si, cuando intervienen varios técnicos, existe un responsable principal.
6. Si los criterios de asignación bloquean la asignación o solo se muestran como apoyo a la decisión.
