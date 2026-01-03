from typing import Optional

from fastapi import status


class ServiceError(Exception):
    """业务异常基类"""

    code: int = 50001
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "内部服务器错误"

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
    message = "用户名或密码错误"


class TokenInvalidError(UnauthorizedError):
    code = 40102
    message = "凭证不可用"


class TokenExpiredError(UnauthorizedError):
    code = 40103
    message = "凭证已过期"


class PermissionDeniedError(ServiceError):
    code = 40301
    status_code = status.HTTP_403_FORBIDDEN
    message = "权限不足"


class NotFoundError(ServiceError):
    code = 40401
    status_code = status.HTTP_404_NOT_FOUND
    message = "没有找到资源"


class ConflictError(ServiceError):
    code = 40901
    status_code = status.HTTP_409_CONFLICT
    message = "Resource conflict"


class ServiceValidationError(ServiceError):
    code = 42201
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
