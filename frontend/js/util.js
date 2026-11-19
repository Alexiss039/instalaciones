// Utilidades de interfaz: creación segura de elementos DOM, etiquetas, fechas, avisos y formularios.
// Todo el texto dinámico se inserta como texto (nunca como HTML) para evitar inyecciones (XSS).

export function h(etiqueta, atributos = {}, ...hijos) {
  const el = document.createElement(etiqueta);
  for (const [clave, valor] of Object.entries(atributos || {})) {
    if (valor === null || valor === undefined || valor === false) continue;
    if (clave === 'class') el.className = valor;
    else if (clave.startsWith('on') && typeof valor === 'function') el.addEventListener(clave.slice(2), valor);
    else el.setAttribute(clave, valor === true ? '' : valor);
  }
  for (const hijo of hijos.flat(Infinity)) {
    if (hijo === null || hijo === undefined || hijo === false) continue;
    el.append(hijo instanceof Node ? hijo : document.createTextNode(String(hijo)));
  }
  return el;
}

export const ETIQUETAS = {
  estado: {
    reportado: 'Reportado', evaluado: 'Evaluado', asignado: 'Asignado', en_atencion: 'En atención',
    en_verificacion: 'En verificación', cerrado: 'Cerrado', rechazado: 'Rechazado', duplicado: 'Duplicado',
  },
  grupo: { pendiente: 'Pendientes', en_atencion: 'En atención', finalizado: 'Finalizados' },
  prioridad: { baja: 'Baja', media: 'Media', alta: 'Alta', critica: 'Crítica' },
  tipo_falla: {
    electrica: 'Eléctrica', iluminacion: 'Iluminación', plomeria: 'Plomería', climatizacion: 'Climatización',
    mobiliario: 'Mobiliario', red_datos: 'Red de datos', estructura: 'Estructura', otra: 'Otra',
  },
  tipo_espacio: { aula: 'Aula', oficina: 'Oficina', laboratorio: 'Laboratorio', zona_comun: 'Zona común', otro: 'Otro' },
  resultado: {
    resuelto: 'Resuelto', no_reproducible: 'No reproducible', requiere_tercero: 'Requiere un tercero',
    no_solucionable: 'No solucionable',
  },
  rol: { reportante: 'Reportante', mantenimiento: 'Mantenimiento', coordinacion: 'Coordinación' },
  cargo: { docente: 'Docente', administrativo: 'Administrativo' },
  rol_asignacion: { responsable: 'Responsable', apoyo: 'Apoyo' },
};

// Estados que pertenecen a cada grupo (igual que GRUPO_DE_ESTADO en backend/app/enums.py).
export const GRUPOS_ESTADOS = {
  pendiente: ['reportado', 'evaluado', 'asignado'],
  en_atencion: ['en_atencion', 'en_verificacion'],
  finalizado: ['cerrado', 'rechazado', 'duplicado'],
};

export const t = (categoria, valor) => ETIQUETAS[categoria]?.[valor] ?? valor ?? '—';

export const opciones = (categoria, { vacio } = {}) => [
  vacio !== undefined && h('option', { value: '' }, vacio),
  ...Object.entries(ETIQUETAS[categoria]).map(([valor, texto]) => h('option', { value: valor }, texto)),
];

export const badge = (categoria, valor) => h('span', { class: `badge b-${valor}` }, t(categoria, valor));

// ---------------------------------------------------------------- Fechas
export function fmtFecha(iso) {
  if (!iso) return '—';
  const [a, m, d] = iso.slice(0, 10).split('-');
  return `${d}/${m}/${a}`;
}

export function fmtFechaHora(iso) {
  if (!iso) return '—';
  // El servidor guarda la hora en UTC sin indicar la zona: se interpreta como UTC y se muestra en hora local.
  const fecha = new Date(/[zZ]|[+-]\d\d:\d\d$/.test(iso) ? iso : `${iso}Z`);
  return fecha.toLocaleString('es-CO', { dateStyle: 'short', timeStyle: 'short' });
}

export const hoy = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

export const recortar = (texto, n = 80) => (texto && texto.length > n ? `${texto.slice(0, n - 1)}…` : texto || '');

// ---------------------------------------------------------------- Avisos y navegación
export function aviso(mensaje, tipo = 'ok') {
  const nodo = h('div', { class: `aviso aviso-${tipo}`, role: tipo === 'error' ? 'alert' : 'status' }, mensaje);
  document.getElementById('avisos').append(nodo);
  setTimeout(() => nodo.remove(), 4500);
}

export const recargarVista = () => window.dispatchEvent(new Event('recargar'));

export function modal(titulo, contenido) {
  const dialogo = h('dialog', { class: 'modal' },
    h('div', { class: 'modal-cab' }, h('h2', {}, titulo),
      h('button', { class: 'btn-icono', type: 'button', 'aria-label': 'Cerrar', onclick: () => dialogo.close() }, '×')),
    contenido);
  dialogo.addEventListener('close', () => dialogo.remove());
  document.body.append(dialogo);
  dialogo.showModal();
  return dialogo;
}

// ---------------------------------------------------------------- Formularios
export function campo(etiqueta, control, ayuda) {
  if (!control.id) control.id = `c${Math.random().toString(36).slice(2, 9)}`;
  return h('div', { class: 'campo' }, h('label', { for: control.id }, etiqueta), control,
    ayuda && h('small', { class: 'ayuda' }, ayuda));
}

// Campo de contraseña con botón de ojo para mostrarla u ocultarla (accesible: aria-pressed y nombre cambiante).
export function campoContrasena(etiqueta, input, ayuda) {
  const campoBase = campo(etiqueta, input, ayuda);
  const boton = h('button', { type: 'button', class: 'ojo', 'aria-label': 'Mostrar contraseña', 'aria-pressed': 'false' }, icono(ICONOS.ojo));
  boton.addEventListener('click', () => {
    const ver = input.type === 'password';
    input.type = ver ? 'text' : 'password';
    boton.setAttribute('aria-pressed', String(ver));
    boton.setAttribute('aria-label', ver ? 'Ocultar contraseña' : 'Mostrar contraseña');
    boton.replaceChildren(icono(ver ? ICONOS.ojoTachado : ICONOS.ojo));
  });
  const envoltura = h('div', { class: 'con-ojo' }, boton);
  input.replaceWith(envoltura);
  envoltura.prepend(input);
  return campoBase;
}

// Exige un correo @gmail.com en el navegador (el servidor sigue validando el formato por su cuenta).
export function exigirGmail(input) {
  const revisar = () => input.setCustomValidity(
    !input.value || /^[^\s@]+@gmail\.com$/i.test(input.value.trim()) ? '' : 'Use un correo @gmail.com');
  input.addEventListener('input', revisar);
  revisar();
  return input;
}

export function mensajesError(error) {
  // Un único error que no es de un campo (p. ej. una regla del proceso): se muestra solo su mensaje.
  if (error.errores?.length === 1 && !error.errores[0].campo) return [h('p', {}, error.errores[0].mensaje)];
  const nodos = [h('p', {}, error.detalle || error.message || 'Ocurrió un error inesperado')];
  if (error.errores?.length) {
    nodos.push(h('ul', {}, error.errores.map((e) => h('li', {}, e.campo ? `${e.campo}: ${e.mensaje}` : e.mensaje))));
  }
  return nodos;
}

// Conecta el envío de un formulario con una acción asíncrona y muestra los errores de la API.
export function manejarFormulario(form, accion) {
  const caja = h('div', { class: 'error', role: 'alert', hidden: true });
  form.prepend(caja);
  form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const boton = form.querySelector('button[type=submit]');
    caja.hidden = true;
    if (boton) boton.disabled = true;
    try {
      await accion(new FormData(form));
    } catch (error) {
      caja.replaceChildren(...mensajesError(error));
      caja.hidden = false;
      caja.scrollIntoView({ block: 'nearest' });
    } finally {
      if (boton?.isConnected) boton.disabled = false;
    }
  });
  return form;
}

export const vacio = (texto) => h('p', { class: 'vacio' }, texto);

// Iconos de línea fina (SVG estático y de confianza: nunca se mezcla con datos del usuario).
export function icono(trazo) {
  const nodo = document.createElement('span');
  nodo.setAttribute('aria-hidden', 'true');
  nodo.style.display = 'contents';
  nodo.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${trazo}</svg>`;
  return nodo;
}
export const ICONOS = {
  usuario: '<circle cx="12" cy="8" r="3.6"/><path d="M4.5 20c.8-3.6 3.8-5.5 7.5-5.5s6.7 1.9 7.5 5.5"/>',
  salir: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5M21 12H9"/>',
  flecha: '<path d="M6 9l6 6 6-6"/>',
  ojo: '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
  ojoTachado: '<path d="M3 3l18 18"/><path d="M10.6 5.1A10.7 10.7 0 0 1 12 5c6.4 0 10 7 10 7a17 17 0 0 1-3.2 4.2M6.3 6.3A17 17 0 0 0 2 12s3.6 7 10 7a10.5 10.5 0 0 0 4.1-.8"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/>',
  llave: '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.1L3.5 17.2a1.8 1.8 0 0 0 2.6 2.6l5.8-5.8a4 4 0 0 0 5.1-5.4l-2.4 2.4-2.1-.4-.4-2.1z"/>',
};

// Entrada escalonada al hacer scroll para tarjetas e indicadores (una sola vez, solo con IntersectionObserver).
let observador;
export function observarEntradas(raiz = document) {
  if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.documentElement.classList.add('js');
  observador ??= new IntersectionObserver((entradas) => entradas.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add('in'); observador.unobserve(e.target); }
  }), { threshold: .08 });
  raiz.querySelectorAll('.tarjeta, .indicador').forEach((el, i) => {
    el.classList.add('rv');
    el.style.setProperty('--i', String(i % 4));
    observador.observe(el);
  });
}
