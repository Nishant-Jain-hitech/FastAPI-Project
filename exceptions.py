from starlette.responses import JSONResponse
from starlette.requests import Request
from sqlalchemy.exc import IntegrityError


def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=400, content={"error": "Kuchh naya la"})


def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Kuchh to gadbad h"})
