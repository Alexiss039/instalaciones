"""Punto de entrada de la API de mantenimiento de instalaciones."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import crear_tablas
from .errores import registrar_manejadores
from .routers import auth, consolidado, espacios, reportes, usuarios


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    crear_tablas()
    yield


app = FastAPI(
    title="API de mantenimiento de instalaciones",
    description="Registro, evaluación, asignación, intervención y cierre de fallas de infraestructura.",
    version="1.0.0",
    lifespan=ciclo_de_vida,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000",
                   "http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)
registrar_manejadores(app)

for modulo in (auth, usuarios, espacios, reportes, consolidado):
    app.include_router(modulo.router)


@app.get("/salud", tags=["Sistema"], summary="Verifica que la API está en ejecución")
def salud():
    return {"estado": "ok"}


# El frontend (carpeta ../frontend) se sirve desde la misma aplicación cuando exista.
_frontend = Path(__file__).resolve().parents[2] / "frontend"
if _frontend.is_dir():
    app.mount("/", StaticFiles(directory=_frontend, html=True), name="frontend")
