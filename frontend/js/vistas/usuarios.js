// Gestión de cuentas (coordinación): crear usuarios de cualquier perfil y administrar disponibilidad.
import { api } from '../api.js';
import { h, t, ETIQUETAS, campo, campoContrasena, exigirGmail, opciones, modal, manejarFormulario, aviso, recargarVista, vacio } from '../util.js';

export async function vistaUsuarios(yo) {
  const usuarios = await api('/usuarios');
  const hecho = (mensaje) => { aviso(mensaje); recargarVista(); };

  function formUsuario(u) {
    const edicion = Boolean(u);
    const rol = h('select', { name: 'rol', disabled: edicion }, opciones('rol'));
    const cargo = h('select', { name: 'cargo' }, opciones('cargo', { vacio: 'Seleccione…' }));
    const especialidades = h('fieldset', { class: 'decision' }, h('legend', {}, 'Especialidades'),
      h('div', { class: 'checks' }, Object.entries(ETIQUETAS.tipo_falla).map(([valor, texto]) => h('label', { class: 'check' },
        h('input', { type: 'checkbox', name: 'especialidades', value: valor, checked: u?.especialidades.includes(valor) }), texto))));
    const experiencia = h('input', { type: 'number', name: 'experiencia', min: 0, max: 60, value: u?.experiencia_anios ?? 0 });
    const bCargo = h('div', {}, campo('Cargo', cargo));
    const bTecnico = h('div', {}, especialidades, campo('Años de experiencia', experiencia));
    if (u) { rol.value = u.rol; cargo.value = u.cargo || ''; }

    const form = h('form', {},
      campo('Nombre completo', h('input', { type: 'text', name: 'nombre', required: true, minlength: 3, maxlength: 120, value: u?.nombre || '' })),
      campo('Correo', exigirGmail(h('input', { type: 'email', name: 'correo', required: !edicion, disabled: edicion, value: u?.correo || '', placeholder: 'nombre@gmail.com' }))),
      campo('Teléfono', h('input', { type: 'tel', name: 'telefono', required: true, pattern: '[0-9+ \\(\\)\\-]{7,20}', value: u?.telefono || '' })),
      campo('Perfil', rol), bCargo, bTecnico,
      edicion ? h('div', { class: 'checks' },
        h('label', { class: 'check' }, h('input', { type: 'checkbox', name: 'disponible', checked: u.disponible }), 'Disponible para nuevas asignaciones'),
        h('label', { class: 'check' }, h('input', { type: 'checkbox', name: 'activo', checked: u.activo, disabled: u.id === yo.id }), 'Cuenta activa')) : null,
      campoContrasena(edicion ? 'Nueva contraseña (opcional)' : 'Contraseña', h('input', { type: 'password', name: 'password', required: !edicion,
        minlength: 8, maxlength: 72, autocomplete: 'new-password' }), 'Mínimo 8 caracteres, con letras y números.'),
      h('button', { class: 'btn', type: 'submit' }, edicion ? 'Guardar cambios' : 'Crear usuario'));

    const actualizar = () => {
      bCargo.hidden = rol.value !== 'reportante';
      cargo.required = rol.value === 'reportante';
      bTecnico.hidden = rol.value !== 'mantenimiento';
    };
    rol.addEventListener('change', actualizar);
    actualizar();

    return manejarFormulario(form, async (fd) => {
      const rolValor = edicion ? u.rol : fd.get('rol');
      const cuerpo = { nombre: fd.get('nombre'), telefono: fd.get('telefono') };
      if (fd.get('password')) cuerpo.password = fd.get('password');
      if (rolValor === 'reportante' && fd.get('cargo')) cuerpo.cargo = fd.get('cargo');
      if (rolValor === 'mantenimiento') {
        cuerpo.especialidades = fd.getAll('especialidades');
        cuerpo.experiencia_anios = Number(fd.get('experiencia') || 0);
      }
      if (edicion) {
        cuerpo.disponible = fd.has('disponible');
        if (u.id !== yo.id) cuerpo.activo = fd.has('activo');
        await api(`/usuarios/${u.id}`, { metodo: 'PATCH', json: cuerpo });
      } else {
        Object.assign(cuerpo, { correo: fd.get('correo'), rol: rolValor });
        await api('/usuarios', { metodo: 'POST', json: cuerpo });
      }
      document.querySelector('dialog')?.close();
      hecho(edicion ? 'Usuario actualizado' : 'Usuario creado');
    });
  }

  const detalle = (u) => (u.rol === 'reportante' ? t('cargo', u.cargo)
    : u.rol === 'mantenimiento' ? `${u.experiencia_anios} años · ${u.especialidades.map((e) => t('tipo_falla', e)).join(', ') || 'sin especialidad'}`
      : '—');

  return h('div', {},
    h('div', { class: 'cabecera' }, h('h1', {}, 'Usuarios'),
      h('button', { class: 'btn', type: 'button', onclick: () => modal('Nuevo usuario', formUsuario()) }, '+ Nuevo usuario')),
    h('section', { class: 'tarjeta' }, usuarios.length ? h('div', { class: 'tabla-scroll' }, h('table', {},
      h('thead', {}, h('tr', {}, ['Nombre', 'Correo', 'Teléfono', 'Perfil', 'Detalle', 'Estado', 'Acciones'].map((c) => h('th', { scope: 'col' }, c)))),
      h('tbody', {}, usuarios.map((u) => h('tr', { class: u.activo ? '' : 'inactivo' },
        h('td', {}, u.nombre), h('td', {}, u.correo), h('td', {}, u.telefono), h('td', {}, t('rol', u.rol)), h('td', {}, detalle(u)),
        h('td', {}, !u.activo ? 'Desactivada' : u.rol === 'mantenimiento' ? (u.disponible ? 'Disponible' : 'No disponible') : 'Activa'),
        h('td', {}, h('button', { class: 'btn btn-sec btn-peq', type: 'button', onclick: () => modal('Editar usuario', formUsuario(u)) }, 'Editar'))))))
    ) : vacio('No hay usuarios.')));
}
