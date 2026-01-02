from typing import TypeVar, Generic, List, Tuple, Type, Union, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base
from app.repositories.base import BaseRepo

T = TypeVar("T", bound=Base)  # ORM 类型


class BaseService(Generic[T]):
    repo: "BaseRepo[T]" = None
    preload_options: list = None  # 预加载关系
    db: AsyncSession
    model: Type[T]

    def __init_subclass__(cls):
        required_attrs = ("repo", "model")
        for attr in required_attrs:
            if getattr(cls, attr, None) is None:
                raise NotImplementedError(f"{cls.__name__}.{attr} must be defined")

    def __init__(self, db: AsyncSession, preload_options: Optional[List] = None):
        self.db = db
        self.preload_options = preload_options or []

        if isinstance(self.repo, type):
            self.repo = self.repo()

    async def get_by_pk(self, pk: int, preload_options: Optional[List] = None) -> T:
        options = preload_options if preload_options is not None else self.preload_options
        return await self.repo.get_by_pk(self.db, pk, preload_options=options)

    async def get_by_pks(self, pks: List[int], preload_options: Optional[List] = None) -> List[T]:
        if not pks:
            return []
        options = preload_options if preload_options is not None else self.preload_options
        return await self.repo.get_by_pks(self.db, pks, preload_options=options)

    async def get_all(self) -> List[T]:
        return await self.repo.get_all(self.db)

    async def get_paged(
            self,
            page: int = 1,
            page_size: int = 10,
            filters: dict | None = None,
            order_by: str | None = None,
            desc: bool = False,
            preload_options: Optional[List] = None,
    ) -> Tuple[List[T], int]:
        options = preload_options if preload_options is not None else self.preload_options
        items, total = await self.repo.get_paged(
            self.db,
            page=page,
            page_size=page_size,
            filters=filters,
            order_by=order_by,
            desc_order=desc,
            preload_options=options
        )
        return items, total

    async def check_before_create(self, data: dict):
        """
        创建前的检查钩子，子类可以重写
        """
        pass

    async def create(
            self,
            data: T | dict,
            commit: bool = True,
            **kwargs
    ) -> T:
        if hasattr(data, "model_dump"):
            attrs = data.model_dump()
        elif isinstance(data, dict):
            attrs = data
        else:
            raise TypeError("data must be a Pydantic model or dict")

        await self.check_before_create(attrs)

        # 排除非自身字段
        model_fields = {c.name for c in self.model.__table__.columns}
        filtered_attrs = {k: v for k, v in attrs.items() if k in model_fields}

        obj = self.model(**filtered_attrs)
        await self.repo.create(self.db, obj)

        if commit:
            await self.db.commit()
            await self.db.refresh(obj)  # 确保 ORM 对象更新了 id 等字段
        return obj

    async def update(self, pk: int, data, commit: bool = True) -> T:
        if hasattr(data, "model_dump"):
            attrs = data.model_dump(exclude_unset=True)
        else:
            attrs = data

        obj = await self.get_by_pk(pk)
        await self.repo.update(self.db, obj, attrs)
        if commit:
            await self.db.commit()
        return obj

    async def delete(self, pk: int, commit: bool = True) -> T:
        obj = await self.repo.delete(self.db, pk)
        if commit:
            await self.db.commit()
        return obj
