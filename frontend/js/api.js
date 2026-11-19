// Cliente de la API REST. El token JWT se guarda solo en sessionStorage (se pierde al cerrar la pestaña).
const BASE = window.API_URL || '';
const CLAVE = 'instalaciones.sesion';

export const sesion = {
  leer() {
    try { return JSON.parse(sessionStorage.getItem(CLAVE)); } catch { return null; }
  },
  guardar(datos) { sessionStorage.setItem(CLAVE, JSON.stringify(datos)); },
  cerrar() { sessionStorage.removeItem(CLAVE); },
};

function traducir(mensaje = '') {
  let r;
  if (mensaje.startsWith('Value error, ')) return mensaje.slice('Value error, '.length);
  if (mensaje === 'Field required') return 'Este campo es obligatorio';
  if ((r = mensaje.match(/at least (\d+) character/))) return `Debe tener al menos ${r[1]} caracteres`;
  if ((r = mensaje.match(/at most (\d+) character/))) return `Debe tener máximo ${r[1]} caracteres`;
  if (/pattern/.test(mensaje)) return 'Formato no válido';
  if (/valid date/.test(mensaje)) return 'Fecha no válida';
  if (/valid integer|valid number/.test(mensaje)) return 'Debe ser un número válido';
  if ((r = mensaje.match(/greater than or equal to (\d+)/))) return `Debe ser mayor o igual a ${r[1]}`;
  if ((r = mensaje.match(/less than or equal to (\d+)/))) return `Debe ser menor o igual a ${r[1]}`;
  if (/Input should be/.test(mensaje)) return 'Valor no permitido';
  return mensaje;
}

export class ErrorApi extends Error {
  constructor(estado, detalle, errores = []) {
    super(detalle);
    this.estado = estado;
    this.detalle = detalle;
    // «body» es el nombre técnico de un error que no es de un campo concreto: no se muestra como etiqueta.
    this.errores = errores.map((e) => ({ campo: e.campo === 'body' ? '' : e.campo, mensaje: traducir(e.mensaje) }));
  }
}

export async function api(ruta, { metodo = 'GET', json, form, archivo, params, respuesta = 'json' } = {}) {
  const url = new URL(BASE + ruta, window.location.origin);
  for (const [clave, valor] of Object.entries(params || {})) {
    if (valor !== '' && valor !== null && valor !== undefined) url.searchParams.set(clave, valor);
  }
  const cabeceras = {};
  const datos = sesion.leer();
  if (datos?.token) cabeceras.Authorization = `Bearer ${datos.token}`;
  let cuerpo;
  if (json !== undefined) { cabeceras['Content-Type'] = 'application/json'; cuerpo = JSON.stringify(json); }
  else if (form) cuerpo = new URLSearchParams(form);
  else if (archivo) cuerpo = archivo;

  let res;
  try {
    res = await fetch(url, { method: metodo, headers: cabeceras, body: cuerpo });
  } catch {
    throw new ErrorApi(0, 'No se pudo conectar con el servidor. Verifique que la API esté en ejecución.');
  }
  if (!res.ok) {
    let cuerpoError = {};
    try { cuerpoError = await res.json(); } catch { /* sin cuerpo JSON */ }
    if (res.status === 401 && datos?.token) {   // sesión vencida o inválida
      sesion.cerrar();
      window.location.hash = '#/login';
    }
    throw new ErrorApi(res.status, cuerpoError.detalle || `Error ${res.status}`, cuerpoError.errores);
  }
  return respuesta === 'blob' ? res.blob() : res.json();
}
