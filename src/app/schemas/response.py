from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar("T")


class Response(GenericModel, Generic[T]):
    """
    接口返回定义
    """
    code: int = 0               # 自定义状态码
    message: str = ""        # 提示信息
    detail: dict = Field(default_factory=dict)
    data: Optional[T] = None    # 返回数据

    # 兼容PyCharm提示
    def __init__(self, *, code: int = 0, message: str = "", detail: dict | None = None, data: T | None = None):
        super().__init__(code=code, message=message, detail=detail or {}, data=data)