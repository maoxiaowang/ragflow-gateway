from starlette import status

from app.core.exceptions import ServiceError


class RAGFlowError(ServiceError):
    """
    RAGFlow 服务异常
    """
    code = 51001
    status_code = status.HTTP_502_BAD_GATEWAY

    def __init__(self, message: str = "RAGFlow request error", code: int = 10001, detail: str = None):
        super().__init__(message=message, code=code, detail=detail)


class RAGFlowTimeoutError(RAGFlowError):
    """
    RAGFlow 请求超时
    """
    code = 51002
    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    message = "RAGFlow service timeout"


class RAGFlowUnavailableError(RAGFlowError):
    """
    RAGFlow 服务不可用
    """
    code = 51003
    status_code = 503
    message = "RAGFlow service unavailable"


class RAGFlowRequestError(RAGFlowError):
    """
    RAGFlow 请求失败异常
    """
    code = 51004
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "RAGFlow request error"


class RAGFlowResponseError(RAGFlowError):
    """
    RAGFlow 返回结果异常
    """
    code = 51005
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    message = "RAGFlow response error"
