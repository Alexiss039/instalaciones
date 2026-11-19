import { api, sesion } from '../api.js';
import { h, campo, campoContrasena, exigirGmail, opciones, manejarFormulario, icono, ICONOS } from '../util.js';

async function iniciarSesion(correo, password) {
  const res = await api('/auth/login', { metodo: 'POST', form: { username: correo, password } });
  sesion.guardar({ token: res.access_token, usuario: res.usuario });
  window.location.hash = '#/reportes';
}

function tarjeta(titulo, ...contenido) {
  return h('main', { class: 'auth', id: 'principal' },
    h('section', { class: 'auth-hero', 'aria-labelledby': 'tituloHeroe' },
      h('i', { class: 'forma f1', 'aria-hidden': 'true' }), h('i', { class: 'forma f2', 'aria-hidden': 'true' }),
      h('i', { class: 'forma f3', 'aria-hidden': 'true' }),
      h('div', { class: 'marca' }, h('span', { class: 'marca-logo' }, icono(ICONOS.llave)), h('span', {}, 'Mantenimiento de instalaciones')),
      h('div', { class: 'auth-contenido' },
        h('h1', { id: 'tituloHeroe' }, 'Cada falla, ', h('span', { class: 'resalta' }, 'atendida'), ' de principio a fin'),
        h('div', { class: 'pasos-auth', 'aria-hidden': 'true' },
          ['Reporta', 'Evalúa', 'Asigna', 'Interviene', 'Cierra'].map((p) => h('span', {}, p))))),
    h('section', { class: 'auth-lado' },
      h('div', { class: 'auth-tarjeta' }, h('h2', {}, titulo), ...contenido)));
}

export function vistaLogin() {
  const form = h('form', { novalidate: false },
    campo('Correo', exigirGmail(h('input', { type: 'email', name: 'correo', required: true, autocomplete: 'username', placeholder: 'nombre@gmail.com' }))),
    campoContrasena('Contraseña', h('input', { type: 'password', name: 'password', required: true, autocomplete: 'current-password', placeholder: 'Ingrese su contraseña' })),
    h('button', { class: 'btn btn-bloque', type: 'submit' }, 'Ingresar'));
  manejarFormulario(form, (fd) => iniciarSesion(fd.get('correo'), fd.get('password')));
  return tarjeta('Iniciar sesión', form,
    h('a', { class: 'btn btn-bloque btn-contorno', href: '#/registro' }, 'Crear una cuenta'));
}

export function vistaRegistro() {
  const form = h('form', {},
    campo('Nombre completo', h('input', { type: 'text', name: 'nombre', required: true, minlength: 3, maxlength: 120, autocomplete: 'name' })),
    campo('Correo', exigirGmail(h('input', { type: 'email', name: 'correo', required: true, autocomplete: 'email', placeholder: 'nombre@gmail.com' }))),
    campo('Teléfono de contacto', h('input', { type: 'tel', name: 'telefono', required: true, pattern: '[0-9+ \\(\\)\\-]{7,20}', autocomplete: 'tel' })),
    campo('Cargo', h('select', { name: 'cargo', required: true }, opciones('cargo', { vacio: 'Seleccione…' }))),
    campoContrasena('Contraseña', h('input', { type: 'password', name: 'password', required: true, minlength: 8, maxlength: 72, autocomplete: 'new-password', placeholder: 'Cree una contraseña' }),
      'Mínimo 8 caracteres, con al menos una letra y un número.'),
    h('button', { class: 'btn btn-bloque', type: 'submit' }, 'Crear cuenta'));
  manejarFormulario(form, async (fd) => {
    const datos = Object.fromEntries(fd);
    await api('/auth/registro', { metodo: 'POST', json: datos });
    await iniciarSesion(datos.correo, datos.password);
  });
  return tarjeta('Crear cuenta', form,
    h('a', { class: 'btn btn-bloque btn-contorno', href: '#/login' }, 'Ya tengo cuenta'));
}
