// Listado de reportes: "Mis reportes", "Mis trabajos" o "Bandeja", según el perfil. El servidor ya filtra lo visible.
import { api } from '../api.js';
import { h, t, ETIQUETAS, GRUPOS_ESTADOS, campo, opciones, badge, fmtFecha, recortar, vacio } from '../util.js';

// «Estado» depende de «Grupo»: con un grupo elegido solo ofrece los estados de ese grupo (así no hay
// combinaciones sin resultados). Sin grupo, muestra todos menos los que ya se llaman igual que un grupo.
const nombresDeGrupo = new Set(Object.values(ETIQUETAS.grupo));
const opcionesEstado = (grupo) => {
  const estados = grupo
    ? GRUPOS_ESTADOS[grupo]
    : Object.keys(ETIQUETAS.estado).filter((valor) => !nombresDeGrupo.has(ETIQUETAS.estado[valor]));
  return [h('option', { value: '' }, 'Todos'),
    ...estados.map((valor) => h('option', { value: valor }, ETIQUETAS.estado[valor]))];
};

// Un clic en cualquier parte de la fila abre el reporte. El enlace del número sigue funcionando solo (teclado y
// lectores de pantalla), y no se abre si se hizo clic en un enlace o botón, con Ctrl/Mayús/Cmd, o al seleccionar texto.
function abrirReporte(ev, id) {
  if (ev.target.closest('a, button') || ev.ctrlKey || ev.metaKey || ev.shiftKey) return;
  if (window.getSelection()?.toString()) return;
  window.location.hash = `#/reportes/${id}`;
}

const LIMITE = 20;
const TITULOS = { reportante: 'Mis reportes', mantenimiento: 'Mis trabajos asignados', coordinacion: 'Bandeja de reportes' };

export async function vistaLista(usuario) {
  const esCoord = usuario.rol === 'coordinacion';
  const [espacios, tecnicos] = esCoord ? await Promise.all([api('/espacios'), api('/tecnicos')]) : [[], []];
  const filtros = { desplazamiento: 0 };
  const zona = h('div');

  const select = (nombre, hijos) => h('select', { name: nombre }, hijos);
  const selGrupo = select('grupo', opciones('grupo', { vacio: 'Todos' }));
  const selEstado = select('estado', opcionesEstado(''));
  const actualizarEstados = () => {
    const previo = selEstado.value;
    selEstado.replaceChildren(...opcionesEstado(selGrupo.value));
    if ([...selEstado.options].some((o) => o.value === previo)) selEstado.value = previo;   // conserva la elección si sigue siendo válida
  };
  selGrupo.addEventListener('change', actualizarEstados);
  const form = h('form', { class: 'filtros' },
    campo('Grupo', selGrupo),
    campo('Estado', selEstado),
    campo('Tipo de falla', select('tipo_falla', opciones('tipo_falla', { vacio: 'Todos' }))),
    esCoord && campo('Prioridad', select('prioridad', opciones('prioridad', { vacio: 'Todas' }))),
    esCoord && campo('Espacio', select('espacio_id', [h('option', { value: '' }, 'Todos'),
      ...espacios.map((e) => h('option', { value: e.id }, `${e.edificio.nombre} · ${e.nombre}`))])),
    esCoord && campo('Responsable', select('tecnico_id', [h('option', { value: '' }, 'Todos'),
      ...tecnicos.map((x) => h('option', { value: x.id }, x.nombre))])),
    campo('Desde', h('input', { type: 'date', name: 'desde' })),
    campo('Hasta', h('input', { type: 'date', name: 'hasta' })),
    h('div', { class: 'filtros-acciones' },
      h('button', { class: 'btn', type: 'submit' }, 'Filtrar'),
      h('button', { class: 'btn btn-sec', type: 'reset' }, 'Limpiar')));

  form.addEventListener('submit', (ev) => {
    ev.preventDefault();
    Object.assign(filtros, Object.fromEntries(new FormData(form)), { desplazamiento: 0 });
    cargar();
  });
  form.addEventListener('reset', () => setTimeout(() => { actualizarEstados(); form.requestSubmit(); }, 0));

  function tabla(lista) {
    if (!lista.length) {
      return vacio(filtros.desplazamiento ? 'No hay más resultados.' : 'No hay reportes que coincidan con los filtros.');
    }
    const pagina = filtros.desplazamiento / LIMITE + 1;
    return h('div', {},
      h('div', { class: 'tabla-scroll' }, h('table', {},
        h('thead', {}, h('tr', {}, ['N.°', 'Espacio', 'Tipo', 'Descripción', 'Estado', 'Prioridad', 'Reportado']
          .map((c) => h('th', { scope: 'col' }, c)))),
        h('tbody', {}, lista.map((r) => h('tr', { class: 'fila-clic', onclick: (ev) => abrirReporte(ev, r.id) },
          h('td', {}, h('a', { class: 'num-reporte', href: `#/reportes/${r.id}`, 'aria-label': `Abrir el reporte ${r.id}` }, `#${r.id}`)),
          h('td', {}, `${r.espacio.edificio.nombre} · ${r.espacio.nombre}`),
          h('td', {}, t('tipo_falla', r.tipo_falla)),
          h('td', { class: 'celda-texto' }, recortar(r.descripcion, 70)),
          h('td', {}, badge('estado', r.estado)),
          h('td', {}, r.prioridad ? badge('prioridad', r.prioridad) : '—'),
          h('td', {}, fmtFecha(r.creado_en)))))),
      ),
      h('div', { class: 'paginacion' },
        h('button', { class: 'btn btn-sec', type: 'button', disabled: filtros.desplazamiento === 0,
          onclick: () => { filtros.desplazamiento -= LIMITE; cargar(); } }, '← Anterior'),
        h('span', {}, `Página ${pagina}`),
        h('button', { class: 'btn btn-sec', type: 'button', disabled: lista.length < LIMITE,
          onclick: () => { filtros.desplazamiento += LIMITE; cargar(); } }, 'Siguiente →')));
  }

  async function cargar() {
    zona.replaceChildren(h('p', { class: 'cargando' }, 'Cargando…'));
    try {
      zona.replaceChildren(tabla(await api('/reportes', { params: { ...filtros, limite: LIMITE } })));
    } catch (error) {
      zona.replaceChildren(h('div', { class: 'error', role: 'alert' }, error.detalle || error.message));
    }
  }

  await cargar();
  return h('div', {},
    h('div', { class: 'cabecera' }, h('h1', {}, TITULOS[usuario.rol]),
      usuario.rol === 'reportante' && h('a', { class: 'btn', href: '#/reportes/nuevo' }, '+ Nuevo reporte')),
    h('section', { class: 'tarjeta', 'aria-label': 'Filtros' }, form),
    h('section', { class: 'tarjeta', 'aria-live': 'polite' }, zona));
}
