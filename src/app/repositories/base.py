from typing import Type, TypeVar, List, Tuple, Generic, Any, Optional

from sqlalchemy import select, inspect, func, Column, desc, asc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import LoaderOption

from app.core.db import Base
from app.core.exceptions import NotFoundError

T = TypeVar("T", bound=Base)


class BaseRepo(Generic[T]):
    """
    Repository 基类
    """
    model: Type[T]
    pk_column: Column

    def __init__(self, model: Type[T]):
        self.model = model
        self.pk_column = inspect(self.model).primary_key[0]

    async def get_by_pk(
        self,
        db: AsyncSession,
        pk: int,
        preload_options: Optional[List[LoaderOption]] = None,
        raise_not_found: bool = True
    ) -> Optional[T]:
        stmt = select(self.model)
        if preload_options:
            stmt = stmt.options(*preload_options)
        stmt = stmt.where(self.pk_column == pk)

        result = await db.execute(stmt)
        obj: Optional[T] = result.scalars().first()

        if not obj and raise_not_found:
            raise NotFoundError(f"{self.model.__name__} {pk} not found")
        return obj

    async def get_by_pks(
        self,
        db: AsyncSession,
        pks: List[int],
        preload_options: Optional[List[LoaderOption]] = None,
        raise_not_found: bool = True
    ) -> List[T]:
        if not pks:
            return []
        stmt = select(self.model).where(self.pk_column.in_(pks))
        if preload_options:
            stmt = stmt.options(*preload_options)
        result = await db.execute(stmt)
        objs: List[T] = result.scalars().all()  # type: ignore
        if raise_not_found:
            missing = set(pks) - {getattr(o, self.pk_column.name) for o in objs}
            if missing:
                raise NotFoundError(f"{self.model.__name__} {missing} not found")
        return objs

    async def get_all(self, db: AsyncSession) -> List[T]:
        stmt = select(self.model)
        result = await db.execute(stmt)
        return result.scalars().all()  # type: ignore

    async def count(self, db: AsyncSession, filters: Optional[dict] = None) -> int:
        stmt = select(func.count(self.pk_column))
        stmt = self._apply_filters(stmt, filters)
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def create(db: AsyncSession, obj: T, commit: bool = False) -> T:
        db.add(obj)
        await db.flush()
        if commit:
            await db.commit()
        return obj

    @staticmethod
    async def bulk_create(db: AsyncSession, objs: List[T], commit: bool = False) -> List[T]:
        db.add_all(objs)
        await db.flush()
        if commit:
            await db.commit()
        return objs

    async def update(self, db: AsyncSession, obj: T, attrs: dict, commit: bool = False) -> T:
        mapper = inspect(self.model)
        for key, value in attrs.items():
            if key not in mapper.columns:
                continue
            col = mapper.columns[key]
            if value is None and not col.nullable:
                continue
            setattr(obj, key, value)
        await db.flush()
        if commit:
            await db.commit()
        return obj

    async def delete(self, db: AsyncSession, pk: int, commit: bool = False) -> T:
        obj = await self.get_by_pk(db, pk)
        await db.delete(obj)
        await db.flush()
        if commit:
            await db.commit()
        return obj

    # ----------------- 分页 / 查询扩展 -----------------
    def _parse_filter(self, key: str, value: Any):
        parts = key.split("__")
        column_name = parts[0]
        op = parts[1] if len(parts) > 1 else "eq"
        column = getattr(self.model, column_name, None)
        if column is None:
            return None
        if op == "eq":
            return column == value
        if op == "like":
            return column.like(f"%{value}%")
        if op == "in":
            if isinstance(value, str):
                value = value.split(",")
            return column.in_(value)
        if op == "gt":
            return column > value
        if op == "lt":
            return column < value
        return None

    def _apply_filters(self, stmt, filters: Optional[dict]):
        if not filters:
            return stmt
        conditions = [cond for k, v in filters.items() if (cond := self._parse_filter(k, v)) is not None]
        if conditions:
            stmt = stmt.where(and_(*conditions))
        return stmt

    def _apply_ordering(self, stmt, order_by: Optional[str], desc_order: bool = False):
        if not order_by:
            return stmt
        column = getattr(self.model, order_by, None)
        if column:
            stmt = stmt.order_by(desc(column) if desc_order else asc(column))
        return stmt

    @staticmethod
    def _apply_preload(stmt, preload_options: Optional[List[LoaderOption]]):
        if preload_options:
            stmt = stmt.options(*preload_options)
        return stmt

    @staticmethod
    def _apply_pagination(stmt, page: int, page_size: int):
        offset = (page - 1) * page_size
        return stmt.offset(offset).limit(page_size)

    async def get_paged(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        filters: Optional[dict] = None,
        order_by: Optional[str] = None,
        desc_order: bool = False,
        preload_options: Optional[List[LoaderOption]] = None
    ) -> Tuple[List[T], int]:
        # 统计总数
        count_stmt = select(func.count(self.pk_column))
        count_stmt = self._apply_filters(count_stmt, filters)
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        # 查询数据
        stmt = select(self.model)
        stmt = self._apply_filters(stmt, filters)
        stmt = self._apply_ordering(stmt, order_by, desc_order)
        stmt = self._apply_preload(stmt, preload_options)
        stmt = self._apply_pagination(stmt, page, page_size)

        result = await db.execute(stmt)
        items: List[T] = result.scalars().all()  # type: ignore
        return items, total
