"""Carga datos ficticios de demostración: edificios, espacios y una cuenta por perfil.

Uso (desde la carpeta backend/):  python -m app.seed
Todos los datos son inventados; las contraseñas son solo para pruebas locales.
"""
from sqlalchemy import select

from . import database
from .enums import Cargo, Rol, TipoEspacio, TipoFalla
from .models import Edificio, Espacio, Usuario
from .seguridad import hashear_password

PASSWORD_DEMO = "Demo1234"

EDIFICIOS = {
    "Bloque A": [("Aula 101", TipoEspacio.AULA, "1"), ("Aula 102", TipoEspacio.AULA, "1"),
                 ("Oficina de Coordinación", TipoEspacio.OFICINA, "2")],
    "Bloque B": [("Laboratorio de Sistemas", TipoEspacio.LABORATORIO, "1"),
                 ("Laboratorio de Redes", TipoEspacio.LABORATORIO, "2")],
    "Zonas comunes": [("Cafetería", TipoEspacio.ZONA_COMUN, "1"), ("Biblioteca", TipoEspacio.ZONA_COMUN, "1"),
                      ("Pasillo principal", TipoEspacio.ZONA_COMUN, "1")],
}

USUARIOS = [
    ("Coordinadora", "coordinacion@gmail.com", "3000000001", Rol.COORDINACION, None, [], 0),
    ("Técnico Eléctrico", "tecnico.electrico@gmail.com", "3000000002", Rol.MANTENIMIENTO, None,
     [TipoFalla.ELECTRICA, TipoFalla.ILUMINACION, TipoFalla.RED_DATOS], 8),
    ("Técnico General", "tecnico.general@gmail.com", "3000000003", Rol.MANTENIMIENTO, None,
     [TipoFalla.PLOMERIA, TipoFalla.MOBILIARIO, TipoFalla.ESTRUCTURA, TipoFalla.CLIMATIZACION], 3),
    ("Docente", "docente@gmail.com", "3000000004", Rol.REPORTANTE, Cargo.DOCENTE, [], 0),
    ("Administrativo", "administrativo@gmail.com", "3000000005", Rol.REPORTANTE,
     Cargo.ADMINISTRATIVO, [], 0),
]


def cargar() -> None:
    database.crear_tablas()
    with database.SesionLocal() as db:
        for nombre_edificio, espacios in EDIFICIOS.items():
            edificio = db.scalar(select(Edificio).where(Edificio.nombre == nombre_edificio))
            if not edificio:
                edificio = Edificio(nombre=nombre_edificio)
                db.add(edificio)
                db.flush()
            for nombre, tipo, piso in espacios:
                existe = db.scalar(select(Espacio).where(Espacio.edificio_id == edificio.id,
                                                         Espacio.nombre == nombre))
                if not existe:
                    db.add(Espacio(edificio_id=edificio.id, nombre=nombre, tipo=tipo, piso=piso))
        for nombre, correo, telefono, rol, cargo, especialidades, experiencia in USUARIOS:
            if not db.scalar(select(Usuario).where(Usuario.correo == correo)):
                db.add(Usuario(nombre=nombre, correo=correo, telefono=telefono, rol=rol, cargo=cargo,
                               password_hash=hashear_password(PASSWORD_DEMO),
                               especialidades=[e.value for e in especialidades],
                               experiencia_anios=experiencia))
        db.commit()
    print("Datos de demostración cargados.")
    print(f"Cuentas (contraseña '{PASSWORD_DEMO}'): " + ", ".join(u[1] for u in USUARIOS))


if __name__ == "__main__":
    cargar()
