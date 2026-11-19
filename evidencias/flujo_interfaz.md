# PF-12 desde la interfaz: flujo completo interfaz → API → base de datos

**Requisitos:** RF-03 a RF-12 · **Criterios:** CA-01 a CA-06 · **Datos:** cuentas ficticias de `python -m app.seed`.

## Preparación

```powershell
cd backend
python -m app.seed
uvicorn app.main:app --port 8000
```

Abrir <http://localhost:8000/>. Para repetir la prueba desde cero, detener el servidor y borrar `backend/instalaciones.db`.

## Resultado de la ejecución

Flujo ejecutado el 19/11/2026 en el navegador contra el servidor local (sin errores en la consola del navegador).
Las capturas de pantalla se guardan en `evidencias/capturas/` con los nombres indicados.

| Paso | Perfil (cuenta) | Acción en la interfaz | Resultado esperado y observado | Captura |
|---|---|---|---|---|
| 1 | Docente (`docente@gmail.com`) | Iniciar sesión | Entra a **Mis reportes**, vacío | `01_mis_reportes.png` |
| 2 | Docente | **Nuevo reporte**: Aula 101, Iluminación, urgencia Alta, descripción y una fotografía | Reporte **#1** en estado *Reportado*, con foto visible (HTTP 201 de `POST /reportes` y de `POST /reportes/1/fotos`) | `02_reporte_creado.png` |
| 3 | Coordinación (`coordinacion@gmail.com`) | Abrir el reporte #1 desde la **Bandeja**; en *Evaluar reporte* elegir **Aceptar**, prioridad Alta | Estado *Evaluado*; se ve el contacto del reportante y aparece el panel de asignación | `03_evaluacion.png` |
| 4 | Coordinación | En *Asignar responsable* elegir al técnico eléctrico (el especialista aparece resaltado, con experiencia, disponibilidad y pendientes) | Estado *Asignado*; el técnico figura como responsable | `04_asignacion.png` |
| 5 | Mantenimiento (`tecnico.electrico@gmail.com`) | En **Mis trabajos** abrir #1; registrar intervención (45 min, actividades, resultado) | Estado *En atención*; la intervención queda a nombre del técnico | `05_intervencion.png` |
| 6 | Mantenimiento | *Finalizar trabajo*: resultado Resuelto y descripción de la solución | Por ser prioridad alta queda *En verificación* | `06_finalizacion.png` |
| 7 | Coordinación | *Verificar cierre* → Aprobar cierre | Estado *Cerrado*; el historial muestra los 6 cambios de estado | `07_cierre.png` |
| 8 | Coordinación | **Dashboard** | 1 reporte, 0 pendientes, 0 en atención, 1 finalizado; falla frecuente: Iluminación; responsable: Técnico Eléctrico | `08_dashboard.png` |

## Casos inválidos a mostrar en la sustentación

| Caso | Cómo provocarlo | Resultado esperado |
|---|---|---|
| Dato inválido en el servidor | Registro con contraseña solo de letras (`sololetrasaqui`) | Mensaje: «La contraseña debe tener al menos una letra y un número» (HTTP 422) |
| Permiso | Con el docente, abrir la dirección `#/dashboard` | «Su perfil no tiene acceso a esta sección» |
| Conflicto de estado | Con coordinación, intentar asignar a quien ya es responsable | Mensaje de HTTP 409 junto al formulario |

## Verificación en base de datos (opcional)

```powershell
cd backend
python -c "import sqlite3; c = sqlite3.connect('instalaciones.db'); print(c.execute('select id, estado, resultado_cierre from reportes').fetchall())"
```

Debe mostrar `[(1, 'cerrado', 'resuelto')]`, lo que confirma que lo hecho en la interfaz quedó persistido.
