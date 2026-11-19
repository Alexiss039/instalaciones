// Enrutador (por hash) y marco de la aplicación según el perfil del usuario.
import { sesion } from './api.js';
import { h, t, icono, ICONOS, observarEntradas } from './util.js';
import { vistaLogin, vistaRegistro } from './vistas/auth.js';
import { vistaLista } from './vistas/lista.js';
import { vistaNuevo } from './vistas/nuevo.js';
import { vistaDetalle } from './vistas/detalle.js';
import { vistaDashboard } from './vistas/dashboard.js';
import { vistaEspacios } from './vistas/espacios.js';
import { vistaUsuarios } from './vistas/usuarios.js';

const raiz = document.getElementById('app');

const RUTAS = [
  { patron: /^#\/login$/, publica: true, vista: () => vistaLogin() },
  { patron: /^#\/registro$/, publica: true, vista: () => vistaRegistro() },
  { patron: /^#\/reportes$/, vista: (u) => vistaLista(u) },
  { patron: /^#\/reportes\/nuevo$/, roles: ['reportante'], vista: (u) => vistaNuevo(u) },
  { patron: /^#\/reportes\/(\d+)$/, vista: (u, m) => vistaDetalle(u, Number(m[1])) },
  { patron: /^#\/dashboard$/, roles: ['coordinacion'], vista: () => vistaDashboard() },
  { patron: /^#\/espacios$/, roles: ['coordinacion'], vista: () => vistaEspacios() },
  { patron: /^#\/usuarios$/, roles: ['coordinacion'], vista: (u) => vistaUsuarios(u) },
];

const MENU = {
  reportante: [['#/reportes', 'Mis reportes'], ['#/reportes/nuevo', 'Nuevo reporte']],
  mantenimiento: [['#/reportes', 'Mis trabajos']],
  coordinacion: [['#/reportes', 'Bandeja'], ['#/dashboard', 'Dashboard'],
    ['#/espacios', 'Espacios'], ['#/usuarios', 'Usuarios']],
};

const cerrarMenu = () => {
  document.body.classList.remove('menu-abierto');
  document.getElementById('burger')?.setAttribute('aria-expanded', 'false');
};

// Menú del usuario: se abre con clic y se cierra al hacer clic fuera o con Escape.
function cerrarMenuUsuario({ devolverFoco = false } = {}) {
  const boton = document.getElementById('menuUsuario');
  const panel = document.getElementById('panelUsuario');
  if (!boton || !panel || panel.hidden) return;
  panel.hidden = true;
  boton.setAttribute('aria-expanded', 'false');
  if (devolverFoco) boton.focus();
}

function alternarMenuUsuario(ev) {
  const panel = document.getElementById('panelUsuario');
  const abrir = panel.hidden;
  panel.hidden = !abrir;
  ev.currentTarget.setAttribute('aria-expanded', String(abrir));
}

function marco(usuario, hash, contenido) {
  const activo = (ruta) => (ruta === '#/reportes' ? /^#\/reportes(\/\d+)?$/.test(hash) : hash === ruta);
  const enlaces = MENU[usuario.rol];
  return h('div', { class: 'marco' },
    h('header', { class: 'barra' },
      h('a', { class: 'marca', href: '#/reportes' }, h('span', { class: 'marca-logo' }, icono(ICONOS.llave)),
        h('span', {}, 'Mantenimiento')),
      h('nav', { 'aria-label': 'Principal' },
        enlaces.map(([ruta, texto]) =>
          h('a', { href: ruta, class: activo(ruta) ? 'activo' : '', 'aria-current': activo(ruta) ? 'page' : null }, texto))),
      h('div', { class: 'usuario' },
        h('button', { class: 'usuario-btn', id: 'menuUsuario', type: 'button', 'aria-haspopup': 'menu', 'aria-expanded': 'false',
          'aria-controls': 'panelUsuario', onclick: alternarMenuUsuario },
        h('span', { class: 'avatar' }, icono(ICONOS.usuario)),
        h('span', { class: 'usuario-nombre' }, usuario.nombre, h('small', {}, t('rol', usuario.rol))),
        h('span', { class: 'chevron' }, icono(ICONOS.flecha))),
        h('div', { class: 'panel-usuario', id: 'panelUsuario', role: 'menu', 'aria-labelledby': 'menuUsuario', hidden: true },
          h('div', { class: 'panel-usuario-cab' }, h('b', {}, usuario.nombre), h('small', {}, usuario.correo)),
          h('button', { class: 'menu-salir', type: 'button', role: 'menuitem', onclick: salir }, icono(ICONOS.salir), 'Cerrar sesión'))),
      h('button', { class: 'hamburguesa', id: 'burger', type: 'button', 'aria-label': 'Abrir menú', 'aria-expanded': 'false',
        onclick: (ev) => {
          const abierto = document.body.classList.toggle('menu-abierto');
          ev.currentTarget.setAttribute('aria-expanded', String(abierto));
        } }, h('i'), h('i'))),
    h('div', { class: 'velo', id: 'velo' },
      ...enlaces.map(([ruta, texto], k) => h('a', { href: ruta, style: `--k:${k + 1}`, onclick: cerrarMenu }, texto)),
      h('button', { type: 'button', style: `--k:${enlaces.length + 1}`, onclick: salir }, 'Cerrar sesión'),
      h('small', {}, `${usuario.nombre} · ${t('rol', usuario.rol)}`)),
    h('main', { id: 'principal', tabindex: '-1' }, contenido));
}

function salir() {
  cerrarMenu();
  sesion.cerrar();
  window.location.hash = '#/login';
}

let version = 0;

async function renderizar() {
  const miVersion = ++version;
  const hash = window.location.hash || '#/reportes';
  const datos = sesion.leer();
  const ruta = RUTAS.find((r) => r.patron.test(hash));
  cerrarMenu();

  if (!ruta) {
    window.location.hash = datos ? '#/reportes' : '#/login';
    return;
  }
  if (!ruta.publica && !datos) { window.location.hash = '#/login'; return; }
  if (ruta.publica && datos) { window.location.hash = '#/reportes'; return; }

  const usuario = datos?.usuario;
  let contenido;
  if (ruta.roles && !ruta.roles.includes(usuario.rol)) {
    contenido = h('div', { class: 'error' }, 'Su perfil no tiene acceso a esta sección.');
  } else {
    raiz.replaceChildren(ruta.publica ? h('p', { class: 'cargando' }, 'Cargando…')
      : marco(usuario, hash, h('p', { class: 'cargando' }, 'Cargando…')));
    try {
      contenido = await ruta.vista(usuario, hash.match(ruta.patron));
    } catch (error) {
      contenido = h('div', { class: 'error', role: 'alert' }, error.detalle || error.message);
    }
  }
  if (miVersion !== version) return;   // el usuario ya navegó a otra pantalla
  raiz.replaceChildren(ruta.publica ? contenido : marco(usuario, hash, contenido));
  window.scrollTo(0, 0);
  observarEntradas(raiz);
  document.title = `${document.querySelector('h1')?.textContent || 'Mantenimiento'} · Instalaciones`;
}

window.addEventListener('hashchange', renderizar);
window.addEventListener('recargar', renderizar);
window.addEventListener('keydown', (ev) => {
  if (ev.key === 'Escape') { cerrarMenu(); cerrarMenuUsuario({ devolverFoco: true }); }
});
document.addEventListener('click', (ev) => { if (!ev.target.closest('.usuario')) cerrarMenuUsuario(); });
renderizar();
