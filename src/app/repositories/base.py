"""
Base Repositories
"""
import warnings
from typing import Type, TypeVar, List, Tuple, Generic, Any, Optional

from sqlalchemy import select, inspect, func, Column, desc, asc, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import LoaderOption

from app.core.db import Base
from app.core.exceptions import NotFoundError

T = TypeVar("T", bound=Base)


# noinspection PyMethodMayBeStatic,PyUnusedLocal

class BaseRepo(Generic[T]):
    model: Type[T]
    pk_column: Column

    def __init__(self, model: Type[T] = None):
        self.model = model or getattr(self, "model", None)
        if self.model is None:
            raise TypeError("You must specify a model")

        pk_columns = list(inspect(self.model).primary_key)
        if not pk_columns:
            raise TypeError(f"{self.model.__name__} must have a primary key")

        if len(pk_columns) > 1:
            warnings.warn(
                f"{self.model.__name__} has a composite primary key, "
                f"but BaseRepo only supports single PK. Using the first PK column: {pk_columns[0].name}"
            )

        self.pk_column = pk_columns[0]

    async def get_by_unique_field(
            self,
            db: AsyncSession,
            field_name: str,
            value: Any,
            preload_options: Optional[List[LoaderOption]] = None,
            raise_not_found: bool = True
    ) -> Optional[T]:
        """
        Get a single object by a unique field (e.g., username, email).

        Args:
            db: AsyncSession
            field_name: the column name on the model
            value: the value to filter
            preload_options: optional SQLAlchemy loader options
            raise_not_found: whether to raise NotFoundError if not found

        Returns:
            Optional[T]: the loaded object or None
        """
        column: Column = getattr(self.model, field_name)
        stmt = select(self.model).where(column == value)
        if preload_options:
            stmt = stmt.options(*preload_options)

        result = await db.execute(stmt)
        obj: Optional[T] = result.scalar_one_or_none()

        if not obj and raise_not_found:
            raise NotFoundError(f"{self.model.__name__} with {field_name}={value} not found.")
        return obj

    async def get_by_pk(
            self,
            db: AsyncSession,
            pk: int | str,
            preload_options: Optional[List[LoaderOption]] = None,
            raise_not_found: bool = True
    ) -> Optional[T]:
        """
        Get an object by its primary key, using get_by_unique_field internally.
        """
        return await self.get_by_unique_field(
            db=db,
            field_name=self.pk_column.key,  # or self.pk_column.name depending on ORM setup
            value=pk,
            preload_options=preload_options,
            raise_not_found=raise_not_found
        )

    async def get_by_pks(
            self,
            db: AsyncSession,
            pks: List[int | str],
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
                raise NotFoundError(f"{self.model.__name__} {missing} not found.")
        return objs

    async def get_or_none(
            self,
            db: AsyncSession,
            *,
            field_name: str,
            value: Any,
            preload_options: Optional[List[LoaderOption]] = None,
    ) -> Optional[T]:
        """
        Get a single object by a unique field, or return None if not found.

        This is a semantic wrapper around `get_by_unique_field` with
        `raise_not_found=False`, useful for service-layer logic where
        "not found" is not an exceptional case.

        Args:
            db: SQLAlchemy AsyncSession
            field_name: Name of the unique column on the model
            value: Value to filter by
            preload_options: Optional SQLAlchemy loader options

        Returns:
            The matched object, or None if not found
        """
        return await self.get_by_unique_field(
            db=db,
            field_name=field_name,
            value=value,
            preload_options=preload_options,
            raise_not_found=False,
        )

    async def get_or_create(
            self,
            db: AsyncSession,
            *,
            field_name: str,
            value: Any,
            defaults: Optional[dict] = None,
    ) -> tuple[T, bool]:
        """
        Get an object by a unique field, or create it if it does not exist.

        This method is safe for concurrent scenarios. It relies on a database
        unique constraint and handles race conditions by catching
        IntegrityError during flush.

        Note:
            - This method performs a `flush()` but does NOT commit the transaction.
            - Transaction boundaries (commit / rollback) should be handled
              by the service layer.

        Args:
            db: SQLAlchemy AsyncSession
            field_name: Name of the unique column on the model
            value: Value of the unique field
            defaults: Additional fields used only when creating the object

        Returns:
            A tuple of (object, created):
                - object: The retrieved or newly created ORM object
                - created: True if the object was created, False if it already existed
        """
        obj = await self.get_or_none(
            db,
            field_name=field_name,
            value=value,
        )
        if obj:
            return obj, False

        defaults = defaults or {}
        data = {field_name: value, **defaults}
        obj = self.model(**data)
        db.add(obj)

        try:
            # Flush to trigger database-level unique constraints
            await db.flush()
            return obj, True
        except IntegrityError:
            # Another transaction may have created the object concurrently
            await db.rollback()

            # Re-fetch the existing object
            obj = await self.get_by_unique_field(
                db,
                field_name=field_name,
                value=value,
                raise_not_found=True,
            )
            return obj, False

    async def get_all(self, db: AsyncSession) -> List[T]:
        stmt = select(self.model)
        result = await db.execute(stmt)
        return result.scalars().all()  # type: ignore

    async def count(self, db: AsyncSession, filters: Optional[dict] = None) -> int:
        stmt = select(func.count(self.pk_column))
        stmt = self._apply_filters(stmt, filters)
        result = await db.execute(stmt)
        return result.scalar_one()

    async def create(self, db: AsyncSession, obj: T) -> T:
        db.add(obj)
        return obj

    async def bulk_create(self, db: AsyncSession, objs: List[T]) -> List[T]:
        db.add_all(objs)
        return objs

    async def update(self, db: AsyncSession, obj: T, attrs: dict) -> T:
        mapper = inspect(self.model)
        for key, value in attrs.items():
            if key not in mapper.columns:
                continue
            col = mapper.columns[key]
            if value is None and not col.nullable:
                continue
            setattr(obj, key, value)
        return obj

    async def delete(self, db: AsyncSession, pk: int) -> T:
        obj = await self.get_by_pk(db, pk)
        await db.delete(obj)
        return obj

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
            *,
            page: int = 1,
            page_size: int = 10,
            filters: Optional[dict] = None,
            order_by: Optional[str] = None,
            desc_order: bool = False,
            preload_options: Optional[List[LoaderOption]] = None
    ) -> Tuple[List[T], int]:
        count_stmt = select(func.count(self.pk_column))
        count_stmt = self._apply_filters(count_stmt, filters)
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = select(self.model)
        stmt = self._apply_filters(stmt, filters)
        stmt = self._apply_ordering(stmt, order_by, desc_order)
        stmt = self._apply_preload(stmt, preload_options)
        stmt = self._apply_pagination(stmt, page, page_size)

        result = await db.execute(stmt)
        items: List[T] = result.scalars().all()  # type: ignore
        return items, total
