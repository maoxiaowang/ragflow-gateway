from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Role
from app.repositories.base import BaseRepo


class UserRepo(BaseRepo[User]):
    def __init__(self):
        super().__init__(User)

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        stmt = await db.execute(select(User).where(User.username == username))
        return stmt.scalar_one_or_none()

    async def create_user(
            self,
            db: AsyncSession,
            username: str,
            password: str,
            roles: Optional[List[Role]] = None,
    ) -> User:
        roles = roles or []
        user = User(username=username, hashed_password=password)
        user.roles.extend(roles)
        await self.create(db, user)
        return user
