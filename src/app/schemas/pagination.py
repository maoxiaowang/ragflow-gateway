from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar("T")


class PageData(GenericModel, Generic[T]):
    """
    分页定义
    """
    total: int
    page: int
    page_size: int
    items: List[T]

    # 兼容PyCharm提示
    def __init__(self, *, total: int, page: int, page_size: int, items: List[T]):
        super().__init__(total=total, page=page, page_size=page_size, items=items)
