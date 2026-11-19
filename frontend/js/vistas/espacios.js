// Mantenimiento del catálogo de edificios y espacios (coordinación).
import { api } from '../api.js';
import { h, t, campo, opciones, modal, manejarFormulario, aviso, recargarVista, vacio } from '../util.js';

export async function vistaEspacios() {
  const [edificios, espacios] = await Promise.all([api('/edificios'), api('/espacios')]);
  const hecho = (mensaje) => { aviso(mensaje); recargarVista(); };

  function formEspacio(espacio) {
    const edificio = h('select', { name: 'edificio_id', required: true }, edificios.map((e) => h('option', { value: e.id }, e.nombre)));
    const tipo = h('select', { name: 'tipo', required: true }, opciones('tipo_espacio'));
    const nombre = h('input', { type: 'text', name: 'nombre', required: true, minlength: 2, maxlength: 100 });
    const piso = h('input', { type: 'text', name: 'piso', maxlength: 20 });
    if (espacio) { edificio.value = espacio.edificio.id; tipo.value = espacio.tipo; nombre.value = espacio.nombre; piso.value = espacio.piso || ''; }
    const form = h('form', {}, campo('Edificio', edificio), campo('Nombre del espacio', nombre),
      h('div', { class: 'fila' }, campo('Tipo', tipo), campo('Piso (opcional)', piso)),
      h('button', { class: 'btn', type: 'submit' }, espacio ? 'Guardar cambios' : 'Crear espacio'));
    return manejarFormulario(form, async (fd) => {
      const cuerpo = { edificio_id: Number(fd.get('edificio_id')), nombre: fd.get('nombre'), tipo: fd.get('tipo') };
      if (fd.get('piso')) cuerpo.piso = fd.get('piso');
      await api(espacio ? `/espacios/${espacio.id}` : '/espacios', { metodo: espacio ? 'PATCH' : 'POST', json: cuerpo });
      document.querySelector('dialog')?.close();
      hecho(espacio ? 'Espacio actualizado' : 'Espacio creado');
    });
  }

  const formEdificio = manejarFormulario(h('form', { class: 'form-linea' },
    campo('Nuevo edificio', h('input', { type: 'text', name: 'nombre', required: true, minlength: 2, maxlength: 100 })),
    h('button', { class: 'btn btn-sec', type: 'submit' }, 'Agregar edificio')), async (fd) => {
    await api('/edificios', { metodo: 'POST', json: { nombre: fd.get('nombre') } });
    hecho('Edificio creado');
  });

  async function alternar(espacio) {
    try {
      await api(`/espacios/${espacio.id}`, { metodo: 'PATCH', json: { activo: !espacio.activo } });
      hecho(espacio.activo ? 'Espacio desactivado' : 'Espacio activado');
    } catch (error) { aviso(error.detalle || error.message, 'error'); }
  }

  const tabla = espacios.length ? h('div', { class: 'tabla-scroll' }, h('table', {},
    h('thead', {}, h('tr', {}, ['Edificio', 'Espacio', 'Tipo', 'Piso', 'Estado', 'Acciones'].map((c) => h('th', { scope: 'col' }, c)))),
    h('tbody', {}, espacios.map((e) => h('tr', { class: e.activo ? '' : 'inactivo' },
      h('td', {}, e.edificio.nombre), h('td', {}, e.nombre), h('td', {}, t('tipo_espacio', e.tipo)), h('td', {}, e.piso || '—'),
      h('td', {}, e.activo ? 'Activo' : 'Inactivo'),
      h('td', { class: 'acciones-fila' },
        h('button', { class: 'btn btn-sec btn-peq', type: 'button', onclick: () => modal('Editar espacio', formEspacio(e)) }, 'Editar'),
        h('button', { class: 'btn btn-sec btn-peq', type: 'button', onclick: () => alternar(e) }, e.activo ? 'Desactivar' : 'Activar'))))))
  ) : vacio('Todavía no hay espacios registrados.');

  return h('div', {},
    h('div', { class: 'cabecera' }, h('h1', {}, 'Edificios y espacios'),
      h('button', { class: 'btn', type: 'button', disabled: !edificios.length, onclick: () => modal('Nuevo espacio', formEspacio()) }, '+ Nuevo espacio')),
    h('section', { class: 'tarjeta' }, h('h2', {}, `Edificios (${edificios.length})`),
      edificios.length ? h('p', { class: 'etiquetas' }, edificios.map((e) => h('span', { class: 'chip' }, e.nombre))) : vacio('Cree primero un edificio.'),
      formEdificio),
    h('section', { class: 'tarjeta' }, h('h2', {}, `Espacios (${espacios.length})`),
      h('p', { class: 'suave' }, 'Un espacio desactivado deja de aparecer para nuevos reportes, pero conserva su historial.'), tabla));
}
