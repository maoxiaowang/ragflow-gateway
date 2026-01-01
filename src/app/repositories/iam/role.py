from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Role
from app.repositories.base import BaseRepo


class RoleRepo(BaseRepo[Role]):
    def __init__(self):
        super().__init__(Role)

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Role]:
        stmt = await db.execute(select(Role).where(Role.name == name))
        return stmt.scalar_one_or_none()

    async def get_or_create(self, db: AsyncSession, name: str) -> Role:
        role = await self.get_by_name(db, name)
        if not role:
            role = Role(name=name)
            await self.create(db, role)
        return role
