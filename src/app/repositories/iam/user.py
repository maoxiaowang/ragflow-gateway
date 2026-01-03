from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import User, Role, auth_user_roles
from app.repositories.base import BaseRepo


class UserRepo(BaseRepo[User]):
    model = User

    async def create_user(
            self,
            db: AsyncSession,
            username: str,
            password: str,
            roles: Optional[List[Role]] = None,
            **kwargs
    ) -> User:
        roles = roles or []
        user = User(
            username=username,
            password=password,
            **kwargs
        )
        user.roles.extend(roles)
        await self.create(db, user)
        return user

    @staticmethod
    def _make_preload_options(load_roles: bool, load_permissions: bool) -> List:
        options = list()
        if load_roles:
            if load_permissions:
                options.append(selectinload(User.roles).selectinload(Role.permissions))
            else:
                options.append(selectinload(User.roles))
        return options

    async def get_by_id(
            self,
            db: AsyncSession,
            user_id: int,
            load_roles: bool = False,
            load_permissions: bool = False
    ) -> Optional[User]:
        preload_options = self._make_preload_options(load_roles, load_permissions)
        return await self.get_by_unique_field(
            db=db,
            field_name=self.pk_column.key,
            value=user_id,
            preload_options=preload_options,
        )

    async def get_by_username(
            self,
            db: AsyncSession,
            username: str,
            load_roles: bool = False,
            load_permissions: bool = False,
            raise_not_found: bool = False,
    ) -> Optional[User]:
        """
        Get user by username with optional roles and permissions preloading
        """
        preload_options = self._make_preload_options(load_roles, load_permissions)
        return await self.get_by_unique_field(
            db=db,
            field_name="username",
            value=username,
            preload_options=preload_options,
            raise_not_found=raise_not_found,
        )

    async def delete(self, db: AsyncSession, user_id: int, hard_delete: bool = False) -> User:
        user = await self.get_by_pk(db, user_id)
        if hard_delete:
            await db.execute(auth_user_roles.delete().where(auth_user_roles.c.user_id == user_id))
            await db.delete(user)
        else:
            user.is_deleted = True
            user.is_active = False
            db.add(user)
        return user

    async def delete_batch(self, db: AsyncSession, user_ids: List[int], hard_delete: bool = False) -> List[User]:
        deleted_users = []
        for uid in user_ids:
            user = await self.delete(db, uid, hard_delete=hard_delete)
            if user:
                deleted_users.append(user)
        return deleted_users