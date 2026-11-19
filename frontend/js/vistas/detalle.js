// Detalle de un reporte y acciones disponibles según el perfil y el estado.
import { api } from '../api.js';
import {
  h, t, badge, campo, opciones, modal, manejarFormulario, aviso, recargarVista, fmtFecha, fmtFechaHora,
  hoy, vacio,
} from '../util.js';

const ESTADOS_ASIGNABLES = ['evaluado', 'asignado', 'en_atencion'];

export async function vistaDetalle(usuario, id) {
  const r = await api(`/reportes/${id}`);
  const esCoord = usuario.rol === 'coordinacion';
  const esTec = usuario.rol === 'mantenimiento';
  const esRep = usuario.rol === 'reportante';
  const activas = r.asignaciones.filter((a) => a.activa);
  const responsable = activas.find((a) => a.rol === 'responsable');
  const soyAsignado = activas.some((a) => a.tecnico.id === usuario.id);
  const soyResponsable = responsable?.tecnico.id === usuario.id;

  const [tecnicos, posibles] = await Promise.all([
    esCoord && ['reportado', ...ESTADOS_ASIGNABLES].includes(r.estado)
      ? api('/tecnicos', { params: { tipo_falla: r.tipo_falla } }) : [],
    esCoord && r.estado === 'reportado' ? api(`/reportes/${id}/posibles-duplicados`) : [],
  ]);

  const lateral = [];
  // ---- Acciones por perfil
  if (esCoord && r.estado === 'reportado') {
    lateral.push(tarjetaAccion('Evaluar reporte', formEvaluacion(r, posibles)));
    lateral.push(tarjetaAccion('Solicitar valoración técnica', formValoracion(r, tecnicos),
      'Si necesita criterio técnico antes de evaluar, pida apoyo a un técnico de mantenimiento.'));
  }
  if (esCoord && ESTADOS_ASIGNABLES.includes(r.estado)) {
    lateral.push(tarjetaAccion(responsable ? 'Reasignar o agregar apoyo' : 'Asignar responsable',
      formAsignar(r, tecnicos, responsable)));
  }
  if (esTec && soyAsignado && ['asignado', 'en_atencion'].includes(r.estado)) {
    lateral.push(tarjetaAccion('Registrar intervención', formIntervencion(r)));
  }
  if (r.estado === 'en_atencion' && (soyResponsable || esCoord)) {
    lateral.push(tarjetaAccion(esCoord ? 'Cerrar directamente' : 'Finalizar trabajo', formFinalizar(r, esCoord),
      r.intervenciones.length ? null : 'Antes de finalizar debe existir al menos una intervención registrada.'));
  }
  if (esCoord && r.estado === 'en_verificacion') {
    lateral.push(tarjetaAccion('Verificar cierre', formVerificacion(r)));
  }

  const valoracionesPendientes = r.valoraciones.filter((v) => v.tecnico.id === usuario.id && !v.fecha_respuesta);

  return h('div', {},
    h('p', { class: 'migas' }, h('a', { href: '#/reportes' }, '← Volver al listado')),
    h('div', { class: 'cabecera' },
      h('h1', {}, `Reporte #${r.id}`),
      h('div', { class: 'etiquetas' }, badge('estado', r.estado), r.prioridad && badge('prioridad', r.prioridad))),
    r.duplicado_de_id && h('div', { class: 'nota' }, 'Este reporte fue marcado como duplicado del ',
      h('a', { href: `#/reportes/${r.duplicado_de_id}` }, `reporte #${r.duplicado_de_id}`),
      r.estado_reporte_original ? ` (estado actual: ${t('estado', r.estado_reporte_original)}).` : '.',
      ' Su información se conserva y el trabajo se atiende en el reporte original.'),
    h('div', { class: 'detalle' },
      h('div', { class: 'col-principal' },
        seccionDatos(r, esRep),
        seccionFotos(r, usuario),
        r.reportantes.length > 1 || (!esRep && r.reportantes.length) ? seccionReportantes(r) : null,
        seccionIntervenciones(r),
        seccionHistorial(r)),
      h('div', { class: 'col-lateral' },
        ...valoracionesPendientes.map((v) => tarjetaAccion('Valoración técnica solicitada', formResponderValoracion(r, v),
          v.indicaciones ? `Indicaciones de coordinación: ${v.indicaciones}` : null)),
        ...lateral,
        seccionAsignaciones(r, esCoord),
        r.valoraciones.length ? seccionValoraciones(r) : null,
        seccionCierre(r))));
}

// ---------------------------------------------------------------- Bloques de información
const tarjeta = (titulo, ...contenido) => h('section', { class: 'tarjeta' }, h('h2', {}, titulo), ...contenido);
const tarjetaAccion = (titulo, form, ayuda) => h('section', { class: 'tarjeta tarjeta-accion' },
  h('h2', {}, titulo), ayuda && h('p', { class: 'suave' }, ayuda), form);
const dato = (etiqueta, valor) => h('div', { class: 'dato' }, h('dt', {}, etiqueta), h('dd', {}, valor ?? '—'));

function seccionDatos(r, esRep) {
  return tarjeta('Información de la falla',
    h('dl', { class: 'datos' },
      dato('Espacio', `${r.espacio.edificio.nombre} · ${r.espacio.nombre} (${t('tipo_espacio', r.espacio.tipo)})`),
      dato('Tipo de falla', t('tipo_falla', r.tipo_falla)),
      dato('Ocurre desde', fmtFecha(r.fecha_inicio_falla)),
      dato('Urgencia indicada', r.urgencia_reportada ? t('prioridad', r.urgencia_reportada) : 'Sin indicar'),
      dato('Reportado el', fmtFechaHora(r.creado_en)),
      dato(esRep ? 'Reportado por' : 'Reportante',
        esRep ? 'Usted' : `${r.creador.nombre} (${t('cargo', r.creador.cargo)}) · ${r.creador.correo} · ${r.creador.telefono}`)),
    h('h3', {}, 'Descripción'), h('p', { class: 'texto' }, r.descripcion),
    r.motivo_rechazo && h('div', { class: 'nota nota-error' }, h('strong', {}, 'Motivo del rechazo: '), r.motivo_rechazo));
}

function seccionFotos(r, usuario) {
  const galeria = h('div', { class: 'galeria' });
  for (const foto of r.fotos) {
    const figura = h('figure', { class: 'foto' }, h('span', { class: 'cargando' }, 'Cargando…'));
    galeria.append(figura);
    api(`/reportes/${r.id}/fotos/${foto.id}`, { respuesta: 'blob' }).then((blob) => {
      const url = URL.createObjectURL(blob);
      const alt = `Fotografía del reporte: ${foto.nombre_original}`;
      figura.replaceChildren(
        h('button', { type: 'button', class: 'foto-btn', 'aria-label': `Ampliar ${foto.nombre_original}`,
          onclick: () => modal(foto.nombre_original, h('img', { class: 'foto-grande', src: url, alt })) },
        h('img', { src: url, alt })),
        h('figcaption', {}, foto.nombre_original));
    }).catch(() => figura.replaceChildren('No se pudo cargar la imagen'));
  }

  const puedeSubir = usuario.rol === 'reportante' && r.creador.id === usuario.id
    && !['cerrado', 'rechazado', 'duplicado'].includes(r.estado) && r.fotos.length < 5;
  let subir = null;
  if (puedeSubir) {
    subir = manejarFormulario(h('form', { class: 'form-linea' },
      campo('Agregar fotografía', h('input', { type: 'file', name: 'archivo', required: true, accept: 'image/jpeg,image/png,image/webp' })),
      h('button', { class: 'btn btn-sec', type: 'submit' }, 'Subir')), async (fd) => {
      const archivo = fd.get('archivo');
      if (archivo.size > 5 * 1024 * 1024) throw new Error('La fotografía supera el máximo de 5 MB');
      const datos = new FormData();
      datos.append('archivo', archivo);
      await api(`/reportes/${r.id}/fotos`, { metodo: 'POST', archivo: datos });
      aviso('Fotografía subida');
      recargarVista();
    });
  }
  return tarjeta('Fotografías', r.fotos.length ? galeria : vacio('Este reporte no tiene fotografías.'), subir);
}

function seccionReportantes(r) {
  return tarjeta(`Personas que reportaron esta falla (${r.reportantes.length})`,
    h('p', { class: 'suave' }, 'Se conservan todos los reportantes para poder contactarlos, aunque el trabajo se atienda una sola vez.'),
    h('div', { class: 'tabla-scroll' }, h('table', {},
      h('thead', {}, h('tr', {}, ['Nombre', 'Cargo', 'Contacto', 'Reporte', 'Fecha'].map((c) => h('th', { scope: 'col' }, c)))),
      h('tbody', {}, r.reportantes.map((x) => h('tr', {},
        h('td', {}, x.usuario.nombre), h('td', {}, t('cargo', x.usuario.cargo)),
        h('td', {}, `${x.usuario.correo} · ${x.usuario.telefono}`),
        h('td', {}, x.es_reporte_original ? `#${x.reporte_id} (original)` : h('a', { href: `#/reportes/${x.reporte_id}` }, `#${x.reporte_id} (duplicado)`)),
        h('td', {}, fmtFechaHora(x.fecha_reporte))))))));
}

function seccionIntervenciones(r) {
  return tarjeta(`Intervenciones (${r.intervenciones.length})`,
    r.intervenciones.length ? h('ol', { class: 'lista-eventos' }, r.intervenciones.map((i) => h('li', {},
      h('div', { class: 'evento-cab' }, h('strong', {}, i.tecnico.nombre),
        h('span', { class: 'suave' }, `${fmtFecha(i.fecha_intervencion)} · ${i.tiempo_minutos} min`)),
      h('p', {}, i.actividades),
      h('p', { class: 'suave' }, `Resultado: ${i.resultado}`)))) : vacio('Aún no se han registrado intervenciones.'));
}

function seccionHistorial(r) {
  return tarjeta('Historial de estados', h('ol', { class: 'lista-eventos' }, r.historial.map((x) => h('li', {},
    h('div', { class: 'evento-cab' },
      h('span', {}, x.estado_anterior ? [badge('estado', x.estado_anterior), ' → '] : null, badge('estado', x.estado_nuevo)),
      h('span', { class: 'suave' }, fmtFechaHora(x.fecha))),
    h('p', { class: 'suave' }, `${x.usuario.nombre}${x.comentario ? ` — ${x.comentario}` : ''}`)))));
}

function seccionAsignaciones(r, esCoord) {
  const filas = r.asignaciones;
  return tarjeta('Asignaciones',
    filas.length ? h('ul', { class: 'lista-simple' }, filas.map((a) => h('li', { class: a.activa ? '' : 'inactivo' },
      h('div', {}, h('strong', {}, a.tecnico.nombre), ` · ${t('rol_asignacion', a.rol)}`,
        a.activa ? '' : ' (retirado)'),
      h('small', { class: 'suave' }, `Desde ${fmtFechaHora(a.fecha_asignacion)}`
        + (a.motivo ? ` — ${a.motivo}` : '') + (a.motivo_retiro ? ` — Retiro: ${a.motivo_retiro}` : '')),
      esCoord && a.activa && a.rol === 'apoyo' && ['asignado', 'en_atencion'].includes(r.estado)
        ? h('button', { class: 'btn btn-sec btn-peq', type: 'button', onclick: () => retirar(r, a) }, 'Retirar') : null)))
      : vacio('Sin responsables asignados.'));
}

function seccionValoraciones(r) {
  return tarjeta('Valoraciones técnicas', h('ul', { class: 'lista-simple' }, r.valoraciones.map((v) => h('li', {},
    h('strong', {}, v.tecnico.nombre),
    h('small', { class: 'suave' }, ` · solicitada ${fmtFechaHora(v.fecha_solicitud)}`),
    v.indicaciones && h('p', { class: 'suave' }, `Indicaciones: ${v.indicaciones}`),
    v.concepto ? h('p', {}, `Concepto: ${v.concepto}`) : h('p', { class: 'suave' }, 'Pendiente de respuesta')))));
}

function seccionCierre(r) {
  if (!r.resultado_cierre) return null;
  return tarjeta(r.estado === 'en_verificacion' ? 'Propuesta de cierre (pendiente de verificación)' : 'Cierre del reporte',
    h('dl', { class: 'datos' },
      dato('Resultado', t('resultado', r.resultado_cierre)),
      dato('Trabajo realizado / solución', r.descripcion_solucion),
      r.motivo_cierre ? dato('Motivo', r.motivo_cierre) : null,
      r.fecha_cierre ? dato('Fecha de cierre', fmtFechaHora(r.fecha_cierre)) : null));
}

// ---------------------------------------------------------------- Formularios de acción
const boton = (texto, clase = '') => h('button', { class: `btn ${clase}`, type: 'submit' }, texto);
const textarea = (nombre, filas = 3, extra = {}) => h('textarea', { name: nombre, rows: filas, ...extra });
const hecho = (mensaje) => { aviso(mensaje); recargarVista(); };

function formEvaluacion(r, posibles) {
  const radio = (valor, texto, marcado) => h('label', { class: 'radio' },
    h('input', { type: 'radio', name: 'decision', value: valor, checked: marcado }), texto);
  const prioridad = h('select', { name: 'prioridad' }, opciones('prioridad'));
  prioridad.value = r.urgencia_reportada || 'media';
  const verificacion = h('select', { name: 'verificacion' },
    h('option', { value: '' }, 'Automática (sí en prioridad alta o crítica)'),
    h('option', { value: 'si' }, 'Sí, requiere verificación'), h('option', { value: 'no' }, 'No requiere'));
  const motivo = textarea('motivo_rechazo', 3, { maxlength: 500 });
  const original = h('input', { type: 'number', name: 'duplicado_de_id', min: 1 });

  const bAceptar = h('div', { 'data-bloque': 'aceptar' },
    campo('Prioridad', prioridad),
    h('label', { class: 'check' }, h('input', { type: 'checkbox', name: 'corresponde', checked: true }),
      'La falla corresponde a las instalaciones'),
    h('label', { class: 'check' }, h('input', { type: 'checkbox', name: 'suficiente', checked: true }),
      'La información del reporte es suficiente'),
    campo('Verificación de coordinación al cerrar', verificacion));
  const bRechazar = h('div', { 'data-bloque': 'rechazar' }, campo('Motivo del rechazo', motivo));
  const bDuplicado = h('div', { 'data-bloque': 'duplicado' },
    campo('Número del reporte original', original),
    posibles.length ? h('div', { class: 'sugerencias' }, h('small', { class: 'suave' }, 'Posibles duplicados (mismo espacio y tipo de falla):'),
      posibles.map((p) => h('button', { type: 'button', class: 'chip', onclick: () => { original.value = p.id; } },
        `#${p.id} · ${t('estado', p.estado)}`))) : h('small', { class: 'suave' }, 'No hay otros reportes abiertos del mismo espacio y tipo.'));

  const form = h('form', {},
    h('fieldset', { class: 'decision' }, h('legend', {}, 'Decisión'),
      radio('aceptar', 'Aceptar', true), radio('rechazar', 'Rechazar'), radio('duplicado', 'Duplicado')),
    bAceptar, bRechazar, bDuplicado, boton('Guardar evaluación'));

  const actualizar = () => {
    const decision = form.querySelector('input[name=decision]:checked').value;
    bAceptar.hidden = decision !== 'aceptar';
    bRechazar.hidden = decision !== 'rechazar';
    bDuplicado.hidden = decision !== 'duplicado';
    motivo.required = decision === 'rechazar';
    original.required = decision === 'duplicado';
  };
  form.addEventListener('change', actualizar);
  actualizar();

  return manejarFormulario(form, async (fd) => {
    const decision = fd.get('decision');
    const cuerpo = { decision };
    if (decision === 'aceptar') {
      Object.assign(cuerpo, { prioridad: fd.get('prioridad'), corresponde_instalaciones: fd.has('corresponde'),
        informacion_suficiente: fd.has('suficiente') });
      if (fd.get('verificacion')) cuerpo.requiere_verificacion = fd.get('verificacion') === 'si';
    } else if (decision === 'rechazar') cuerpo.motivo = fd.get('motivo_rechazo');
    else cuerpo.duplicado_de_id = Number(fd.get('duplicado_de_id'));
    await api(`/reportes/${r.id}/evaluacion`, { metodo: 'POST', json: cuerpo });
    hecho('Evaluación registrada');
  });
}

function formValoracion(r, tecnicos) {
  const form = h('form', {},
    campo('Técnico', h('select', { name: 'tecnico_id', required: true }, h('option', { value: '' }, 'Seleccione…'),
      tecnicos.map((x) => h('option', { value: x.id }, `${x.nombre}${x.coincide_especialidad ? ' (especialista en este tipo)' : ''}`)))),
    campo('Indicaciones (opcional)', textarea('indicaciones', 2, { maxlength: 500 })),
    boton('Solicitar valoración', 'btn-sec'));
  return manejarFormulario(form, async (fd) => {
    const cuerpo = { tecnico_id: Number(fd.get('tecnico_id')) };
    if (fd.get('indicaciones')) cuerpo.indicaciones = fd.get('indicaciones');
    await api(`/reportes/${r.id}/valoraciones`, { metodo: 'POST', json: cuerpo });
    hecho('Valoración solicitada');
  });
}

function formResponderValoracion(r, v) {
  return manejarFormulario(h('form', {},
    campo('Su concepto técnico', textarea('concepto', 4, { required: true, minlength: 10, maxlength: 1000 })),
    boton('Enviar concepto')), async (fd) => {
    await api(`/reportes/${r.id}/valoraciones/${v.id}/respuesta`, { metodo: 'POST', json: { concepto: fd.get('concepto') } });
    hecho('Concepto enviado');
  });
}

function formAsignar(r, tecnicos, responsable) {
  const yaAsignados = new Set(r.asignaciones.filter((a) => a.activa).map((a) => a.tecnico.id));
  const rol = h('select', { name: 'rol' }, h('option', { value: 'responsable' }, 'Responsable'),
    responsable ? h('option', { value: 'apoyo' }, 'Apoyo') : null);
  const motivo = textarea('motivo', 2, { maxlength: 500 });
  const tabla = h('div', { class: 'tabla-scroll' }, h('table', { class: 'compacta' },
    h('thead', {}, h('tr', {}, ['Técnico', 'Especialidades', 'Exp.', 'Disp.', 'Pend.'].map((c) => h('th', { scope: 'col' }, c)))),
    h('tbody', {}, tecnicos.map((x) => h('tr', { class: x.coincide_especialidad ? 'coincide' : '' },
      h('td', {}, x.nombre),
      h('td', {}, x.especialidades.length ? x.especialidades.map((e) => t('tipo_falla', e)).join(', ') : '—'),
      h('td', {}, `${x.experiencia_anios} a.`),
      h('td', {}, x.disponible ? 'Sí' : 'No'),
      h('td', {}, x.trabajos_pendientes))))));

  const form = h('form', {},
    h('p', { class: 'suave' }, `Criterios de elección para una falla de tipo "${t('tipo_falla', r.tipo_falla)}": `
      + 'especialidad, experiencia, disponibilidad y trabajos pendientes. Resaltados, los técnicos especialistas.'),
    tabla,
    campo('Técnico', h('select', { name: 'tecnico_id', required: true }, h('option', { value: '' }, 'Seleccione…'),
      tecnicos.filter((x) => !yaAsignados.has(x.id)).map((x) => h('option', { value: x.id, disabled: !x.disponible },
        `${x.nombre} · ${x.trabajos_pendientes} pendientes${x.disponible ? '' : ' · no disponible'}`)))),
    campo('Rol en el reporte', rol),
    campo(responsable ? 'Motivo (obligatorio si cambia al responsable)' : 'Motivo (opcional)', motivo),
    boton(responsable ? 'Asignar' : 'Asignar responsable'));
  const actualizar = () => { motivo.required = Boolean(responsable) && rol.value === 'responsable'; };
  rol.addEventListener('change', actualizar);
  actualizar();

  return manejarFormulario(form, async (fd) => {
    const cuerpo = { tecnico_id: Number(fd.get('tecnico_id')), rol: fd.get('rol') };
    if (fd.get('motivo')) cuerpo.motivo = fd.get('motivo');
    await api(`/reportes/${r.id}/asignaciones`, { metodo: 'POST', json: cuerpo });
    hecho('Asignación guardada');
  });
}

function retirar(r, asignacion) {
  const form = manejarFormulario(h('form', {},
    h('p', {}, `Se retirará a ${asignacion.tecnico.nombre} del reporte #${r.id}.`),
    campo('Motivo', textarea('motivo', 3, { required: true, minlength: 5, maxlength: 500 })),
    boton('Retirar')), async (fd) => {
    await api(`/reportes/${r.id}/asignaciones/${asignacion.id}/retiro`, { metodo: 'POST', json: { motivo: fd.get('motivo') } });
    dialogo.close();
    hecho('Asignación retirada');
  });
  const dialogo = modal('Retirar personal de apoyo', form);
}

function formIntervencion(r) {
  return manejarFormulario(h('form', {},
    h('div', { class: 'fila' },
      campo('Fecha', h('input', { type: 'date', name: 'fecha', required: true, value: hoy(), max: hoy(), min: r.fecha_inicio_falla })),
      campo('Tiempo empleado (min)', h('input', { type: 'number', name: 'tiempo', required: true, min: 1, max: 1440 }))),
    campo('Actividades realizadas', textarea('actividades', 3, { required: true, minlength: 5, maxlength: 2000 })),
    campo('Resultado de la intervención', h('input', { type: 'text', name: 'resultado', required: true, minlength: 3, maxlength: 1000 })),
    boton('Registrar intervención')), async (fd) => {
    await api(`/reportes/${r.id}/intervenciones`, { metodo: 'POST', json: {
      fecha_intervencion: fd.get('fecha'), actividades: fd.get('actividades'),
      tiempo_minutos: Number(fd.get('tiempo')), resultado: fd.get('resultado') } });
    hecho('Intervención registrada');
  });
}

function formFinalizar(r, esCoord) {
  const resultado = h('select', { name: 'resultado' }, opciones('resultado'));
  const motivo = textarea('motivo', 2, { maxlength: 500 });
  const campoMotivo = campo('Motivo (obligatorio si no queda resuelta)', motivo);
  const form = h('form', {},
    campo('Resultado', resultado),
    campo('Trabajo realizado / solución', textarea('solucion', 3, { required: true, minlength: 10, maxlength: 2000 })),
    campoMotivo,
    h('p', { class: 'suave' }, esCoord ? 'Como coordinación, el reporte se cierra directamente.'
      : 'Si la prioridad es alta o el resultado no es "Resuelto", coordinación deberá verificar el cierre.'),
    boton(esCoord ? 'Cerrar reporte' : 'Informar finalización', r.intervenciones.length ? '' : 'btn-sec'));
  const actualizar = () => {
    const exige = resultado.value !== 'resuelto';
    motivo.required = exige;
    campoMotivo.classList.toggle('requerido', exige);
  };
  resultado.addEventListener('change', actualizar);
  actualizar();
  return manejarFormulario(form, async (fd) => {
    const cuerpo = { resultado: fd.get('resultado'), descripcion_solucion: fd.get('solucion') };
    if (fd.get('motivo')) cuerpo.motivo = fd.get('motivo');
    await api(`/reportes/${r.id}/finalizar`, { metodo: 'POST', json: cuerpo });
    hecho('Finalización registrada');
  });
}

function formVerificacion(r) {
  const comentario = textarea('comentario', 3, { maxlength: 500 });
  const form = h('form', {},
    h('p', {}, h('strong', {}, `Propuesta: ${t('resultado', r.resultado_cierre)}. `), r.descripcion_solucion),
    h('fieldset', { class: 'decision' }, h('legend', {}, 'Decisión'),
      h('label', { class: 'radio' }, h('input', { type: 'radio', name: 'aprobado', value: 'si', checked: true }), 'Aprobar cierre'),
      h('label', { class: 'radio' }, h('input', { type: 'radio', name: 'aprobado', value: 'no' }), 'Devolver a atención')),
    campo('Comentario (obligatorio si lo devuelve)', comentario),
    boton('Guardar verificación'));
  form.addEventListener('change', () => { comentario.required = form.querySelector('input[name=aprobado]:checked').value === 'no'; });
  return manejarFormulario(form, async (fd) => {
    const cuerpo = { aprobado: fd.get('aprobado') === 'si' };
    if (fd.get('comentario')) cuerpo.comentario = fd.get('comentario');
    await api(`/reportes/${r.id}/verificacion`, { metodo: 'POST', json: cuerpo });
    hecho('Verificación registrada');
  });
}
