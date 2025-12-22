"""
数据序列化模型
Data Transfer Object
"""

from .response import Response
from .pagination import PageData

__all__ = [
    "Response",
    "PageData",
]
