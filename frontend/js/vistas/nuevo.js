// Formulario para registrar una falla (perfil reportante).
import { api } from '../api.js';
import { h, campo, opciones, manejarFormulario, hoy, aviso } from '../util.js';

const MAX_FOTOS = 5;
const MAX_MB = 5;

export async function vistaNuevo() {
  const espacios = await api('/espacios', { params: { activo: 'true' } });
  const porEdificio = new Map();
  for (const e of espacios) {
    if (!porEdificio.has(e.edificio.nombre)) porEdificio.set(e.edificio.nombre, []);
    porEdificio.get(e.edificio.nombre).push(e);
  }

  const descripcion = h('textarea', { name: 'descripcion', rows: 5, required: true, minlength: 10, maxlength: 1000 });
  const contador = h('small', { class: 'ayuda', 'aria-live': 'off' }, '0 / 1000');
  descripcion.addEventListener('input', () => { contador.textContent = `${descripcion.value.length} / 1000`; });

  const form = h('form', { class: 'form-ancho' },
    campo('Espacio donde ocurre la falla', h('select', { name: 'espacio_id', required: true },
      h('option', { value: '' }, 'Seleccione un espacio…'),
      [...porEdificio].map(([edificio, lista]) => h('optgroup', { label: edificio },
        lista.map((e) => h('option', { value: e.id }, e.nombre)))))),
    h('div', { class: 'fila' },
      campo('Tipo de falla', h('select', { name: 'tipo_falla' }, opciones('tipo_falla'))),
      campo('Urgencia (opcional)', h('select', { name: 'urgencia_reportada' },
        opciones('prioridad', { vacio: 'Sin indicar' }).filter((o) => o.value !== 'critica'))),
      campo('¿Desde cuándo ocurre?', h('input', { type: 'date', name: 'fecha_inicio_falla', required: true, max: hoy(), value: hoy() }))),
    campo('¿Qué está pasando?', descripcion),
    contador,
    campo('Fotografías (opcional)', h('input', { type: 'file', name: 'fotos', accept: 'image/jpeg,image/png,image/webp', multiple: true })),
    h('div', { class: 'acciones' },
      h('button', { class: 'btn', type: 'submit' }, 'Enviar reporte'),
      h('a', { class: 'btn btn-sec', href: '#/reportes' }, 'Cancelar')));

  manejarFormulario(form, async (fd) => {
    const fotos = fd.getAll('fotos').filter((f) => f.size > 0);
    if (fotos.length > MAX_FOTOS) throw new Error(`Máximo ${MAX_FOTOS} fotografías por reporte`);
    const grande = fotos.find((f) => f.size > MAX_MB * 1024 * 1024);
    if (grande) throw new Error(`"${grande.name}" supera el máximo de ${MAX_MB} MB`);

    const cuerpo = {
      espacio_id: Number(fd.get('espacio_id')), tipo_falla: fd.get('tipo_falla'),
      descripcion: fd.get('descripcion'), fecha_inicio_falla: fd.get('fecha_inicio_falla'),
    };
    if (fd.get('urgencia_reportada')) cuerpo.urgencia_reportada = fd.get('urgencia_reportada');
    const reporte = await api('/reportes', { metodo: 'POST', json: cuerpo });

    let fallidas = 0;
    for (const foto of fotos) {
      const datos = new FormData();
      datos.append('archivo', foto);
      try { await api(`/reportes/${reporte.id}/fotos`, { metodo: 'POST', archivo: datos }); } catch { fallidas += 1; }
    }
    aviso(`Reporte #${reporte.id} registrado`);
    if (fallidas) aviso(`${fallidas} fotografía(s) no se pudieron subir; puede agregarlas desde el detalle`, 'error');
    window.location.hash = `#/reportes/${reporte.id}`;
  });

  return h('div', {},
    h('div', { class: 'cabecera cabecera-centrada' }, h('h1', {}, 'Nuevo reporte de falla')),
    h('section', { class: 'tarjeta tarjeta-form' }, form));
}
