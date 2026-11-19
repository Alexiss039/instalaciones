// Dashboard para coordinación: totales, fallas frecuentes, espacios afectados y responsables, con filtro por fechas.
import { api } from '../api.js';
import { h, t, campo, vacio, observarEntradas } from '../util.js';

export async function vistaDashboard() {
  const filtros = {};
  const zona = h('div');

  const form = h('form', { class: 'filtros' },
    campo('Desde', h('input', { type: 'date', name: 'desde' })),
    campo('Hasta', h('input', { type: 'date', name: 'hasta' })),
    h('div', { class: 'filtros-acciones' },
      h('button', { class: 'btn', type: 'submit' }, 'Consultar'),
      h('button', { class: 'btn btn-sec', type: 'reset' }, 'Limpiar')));
  form.addEventListener('submit', (ev) => { ev.preventDefault(); Object.assign(filtros, Object.fromEntries(new FormData(form))); cargar(); });
  form.addEventListener('reset', () => setTimeout(() => form.requestSubmit(), 0));

  const total = (r, grupo) => r.por_grupo.find((g) => g.clave === grupo)?.total || 0;

  const indicador = (texto, valor, clase = '') => h('div', { class: `indicador ${clase}` },
    h('span', { class: 'indicador-valor' }, valor), h('span', { class: 'indicador-texto' }, texto));

  function barras(titulo, lista, etiqueta = (x) => x.etiqueta, clase = '') {
    const maximo = Math.max(1, ...lista.map((x) => x.total));
    return h('section', { class: `tarjeta ${clase}` }, h('h2', {}, titulo),
      lista.length ? h('ul', { class: 'barras' }, lista.map((x) => h('li', {},
        h('span', { class: 'barra-etiqueta' }, etiqueta(x)),
        h('span', { class: 'barra-pista', role: 'presentation' },
          h('span', { class: 'barra-relleno', style: `width:${Math.round((x.total / maximo) * 100)}%` })),
        h('span', { class: 'barra-valor' }, x.total))))
        : vacio('Sin datos en el periodo seleccionado.'));
  }

  async function cargar() {
    zona.replaceChildren(h('p', { class: 'cargando' }, 'Cargando…'));
    try {
      const r = await api('/dashboard/resumen', { params: filtros });
      // Bento sin huecos: fila 1 = 3+3+3+3, fila 2 = 5+4+3, fila 3 = 7+5 (12 columnas exactas)
      zona.replaceChildren(
        h('div', { class: 'bento' },
          indicador('Reportes en el periodo', r.total_reportes, 'k3 ind-total'),
          indicador('Pendientes', total(r, 'pendiente'), 'k3 ind-pendiente'),
          indicador('En atención', total(r, 'en_atencion'), 'k3 ind-atencion'),
          indicador('Finalizados', total(r, 'finalizado'), 'k3 ind-final'),
          barras('Reportes por estado', r.por_estado, (x) => t('estado', x.clave), 'k5'),
          barras('Fallas más frecuentes', r.fallas_mas_frecuentes, (x) => t('tipo_falla', x.clave), 'k4'),
          barras('Resultados de cierre', r.por_resultado_cierre, (x) => t('resultado', x.clave), 'k3'),
          barras('Espacios afectados', r.espacios_afectados, undefined, 'k7'),
          barras('Reportes por responsable', r.por_responsable, undefined, 'k5')));
      observarEntradas(zona);
    } catch (error) {
      zona.replaceChildren(h('div', { class: 'error', role: 'alert' }, error.detalle || error.message));
    }
  }

  await cargar();
  return h('div', {},
    h('div', { class: 'cabecera' }, h('h1', {}, 'Dashboard')),
    h('section', { class: 'tarjeta', 'aria-label': 'Filtro por fechas' }, form),
    h('div', { 'aria-live': 'polite' }, zona));
}
