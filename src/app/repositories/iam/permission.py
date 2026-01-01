from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Permission
from app.repositories.base import BaseRepo


class PermissionRepo(BaseRepo[Permission]):
    def __init__(self):
        super().__init__(Permission)

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Permission]:
        stmt = await db.execute(select(Permission).where(Permission.name == name))
        return stmt.scalar_one_or_none()

    async def get_or_create(self, db: AsyncSession, name: str) -> Permission:
        perm = await self.get_by_name(db, name)
        if not perm:
            perm = Permission(name=name)
            await self.create(db, perm)
        return perm
