from datetime import datetime, timezone
from typing import List, Optional

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Role, Permission
from app.models.auth import InviteCode
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
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        stmt = await db.execute(select(User).where(User.username == username))
        return stmt.scalar_one_or_none()

    async def authenticate(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        user = await self.get_by_username(db, username)
        if user and self.verify_password(password, user.hashed_password):
            return user
        return None

    async def create_user(
        self,
        db: AsyncSession,
        username: str,
        password: str,
        roles: Optional[List[Role]] = None,
        commit: bool = False
    ) -> User:
        """创建用户，可选分配角色，默认自动提交"""
        roles = roles or []
        hashed = self.get_password_hash(password)
        user = User(username=username, hashed_password=hashed)
        user.roles.extend(roles)
        await self.create(db, user)  # BaseRepo.create 只是 add
        if commit:
            await db.commit()
            await db.refresh(user)
        return user


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


class InviteCodeRepo(BaseRepo[InviteCode]):
    def __init__(self):
        super().__init__(InviteCode)

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Optional[InviteCode]:
        stmt = await db.execute(select(InviteCode).where(InviteCode.code == code))
        return stmt.scalar_one_or_none()

    @classmethod
    async def mark_used(cls, db: AsyncSession, invite: InviteCode, user_id: int, commit: bool = False):
        invite.used = True
        invite.used_by = user_id
        invite.used_at = datetime.now(timezone.utc)
        db.add(invite)
        if commit:
            await db.commit()
