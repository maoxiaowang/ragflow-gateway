from app.core.exceptions import ServiceError


class RAGFlowError(ServiceError):
    """
    RAGFlow 客户端异常
    """

    def __init__(self, message: str = "RAGFlow request error", code: int = 10001, detail: str = None):
        super().__init__(message=message, code=code, detail=detail)


class RequestError(RAGFlowError):
    """
    RAGFlow 后端请求失败异常
    """
    pass


class ResponseError(RAGFlowError):
    """
    RAGFlow 后端返回结果异常
    """
    pass
