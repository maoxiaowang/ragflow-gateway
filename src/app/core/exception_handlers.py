import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import ServiceError
from app.core.settings import settings

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": 42201,
                "message": "request validation error",
                "detail": exc.errors(),
                "data": None
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": 50002,
                "message": exc.detail,
                "detail": None,
                "data": None
            }
        )

    @app.exception_handler(ServiceError)
    async def service_error_handler(request: Request, exc: ServiceError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail if settings.debug else None,
                "data": None
            }
        )

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        logger.error("Unexpected error", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 50003,
                "message": "internal server error",
                "detail": str(exc) if settings.debug else None,     # 生产隐藏细节
                "data": None
            }
        )