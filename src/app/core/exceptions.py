from typing import Optional

from fastapi import status


class ServiceError(Exception):
    """业务异常基类"""

    code: int = 10000
    status_code: int = status.HTTP_400_BAD_REQUEST
    message: str = "Service error"

    def __init__(
            self,
            message: Optional[str] = None,
            detail: Optional[str] = None,
            code: Optional[int] = None,
            status_code: Optional[int] = None,
    ):
        if message:
            self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code

        self.detail = detail


class UnauthorizedError(ServiceError):
    code = 40101
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Authentication failed"


class PermissionDeniedError(ServiceError):
    code = 40301
    status_code = status.HTTP_403_FORBIDDEN
    message = "Permission denied"


class NotFoundError(ServiceError):
    code = 40401
    status_code = status.HTTP_404_NOT_FOUND
    message = "Resource not found"


class ConflictError(ServiceError):
    code = 40901
    status_code = status.HTTP_409_CONFLICT
    message = "Resource conflict"


class ValidationError(ServiceError):
    code = 42201
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    message = "Invalid data"
