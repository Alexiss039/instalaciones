"""Errores controlados: respuestas JSON uniformes {"detalle": ..., "codigo": ...}."""
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

registro = logging.getLogger("instalaciones")


def no_encontrado(que: str = "Recurso") -> HTTPException:
    return HTTPException(404, f"{que} no encontrado")


def conflicto(mensaje: str) -> HTTPException:
    return HTTPException(409, mensaje)


def prohibido(mensaje: str = "No tiene permiso para realizar esta acción") -> HTTPException:
    return HTTPException(403, mensaje)


def regla_negocio(mensaje: str) -> HTTPException:
    return HTTPException(422, mensaje)


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException):
        return JSONResponse({"detalle": exc.detail, "codigo": exc.status_code},
                            status_code=exc.status_code, headers=getattr(exc, "headers", None))

    @app.exception_handler(RequestValidationError)
    async def _validacion(_: Request, exc: RequestValidationError):
        errores = [{"campo": ".".join(str(p) for p in e["loc"][1:]) or str(e["loc"][0]),
                    "mensaje": e["msg"]} for e in exc.errors()]
        return JSONResponse({"detalle": "Datos inválidos", "codigo": 422, "errores": errores},
                            status_code=422)

    @app.exception_handler(Exception)
    async def _inesperado(_: Request, exc: Exception):
        registro.exception("Error no controlado", exc_info=exc)  # el detalle queda solo en el log
        return JSONResponse({"detalle": "Error interno del servidor", "codigo": 500}, status_code=500)
