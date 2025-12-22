from typing import List

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Role, Permission
from app.repositories.base import BaseRepo

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    deprecated="auto"
)


class UserRepo(BaseRepo[User]):
    def __init__(self):
        super().__init__(User)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> User | None:
        stmt = await db.execute(
            select(User).where(User.username == username)
        )
        user = stmt.scalar_one_or_none()
        return user

    async def authenticate(self, db: AsyncSession, username: str, password: str) -> User | None:
        user = await self.get_by_username(db, username)
        if user and self.verify_password(password, user.hashed_password):
            return user
        return None

    async def create_user(self, db: AsyncSession, username: str, password: str, roles: List[Role] = []) -> User:
        hashed = self.get_password_hash(password)
        user = User(username=username, hashed_password=hashed, roles=roles)
        await self.create(db, user)
        return user


class RoleRepo(BaseRepo[Role]):
    def __init__(self):
        super().__init__(Role)

    async def get_by_name(self, db: AsyncSession, name: str) -> Role:
        stmt = await db.execute(
            select(Role).where(Role.name == name)
        )
        role = stmt.scalar_one_or_none()
        return role


class PermissionRepo(BaseRepo[Permission]):
    def __init__(self):
        super().__init__(Permission)

    async def get_by_name(self, db: AsyncSession, name: str) -> Permission:
        stmt = await db.execute(
            select(Permission).where(Permission.name == name)
        )
        perm = stmt.scalar_one_or_none()
        return perm
