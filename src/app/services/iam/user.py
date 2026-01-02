from typing import List, Optional

from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import pwd_context
from app.models import User, Role, auth_user_roles
from app.repositories.iam.role import RoleRepo
from app.repositories.iam.user import UserRepo
from app.services.base import BaseService


class UserService(BaseService[User]):
    repo = UserRepo()
    role_repo = RoleRepo()
    model = User

    async def check_before_create(self, data: dict):
        # Ensure username unique
        username = data.get("username")
        if username:
            user = await self.repo.get_by_username(self.db, username)
            if user:
                raise ConflictError(f"Username '{username}' already exists")

    async def create(self, data, roles: Optional[List[Role]] = None, commit: bool=True):
        roles = roles or []
        await self.check_before_create(data)
        username = data.pop("username")
        password = data.pop("password")
        hashed_password = pwd_context.hash(password)
        user = await self.repo.create_user(
            self.db, username=username, password=hashed_password, roles=roles, **data
        )
        if commit:
            await self.db.commit()
        return user

    async def list_roles_for_user(self, user_id: int) -> List[Role]:
        user = await self.repo.get_by_pk(self.db, user_id, preload_options=[selectinload(User.roles)])
        return user.roles if user else []

    async def assign_roles(self, user_id: int, role_ids: List[int], commit: bool = True) -> List[Role]:
        """Assign roles to a user, overwrite existing ones"""
        user = await self.repo.get_by_pk(self.db, user_id)
        if not user:
            raise NotFoundError(f"User with ID '{user_id}' not found")

        roles = await self.role_repo.get_by_pks(self.db, role_ids)
        if len(roles) != len(role_ids):
            raise NotFoundError("Some roles not found")

        # clear existing roles
        await self.db.execute(
            auth_user_roles.delete().where(auth_user_roles.c.user_id == user_id)
        )

        # add new roles
        if roles:
            await self.db.execute(
                auth_user_roles.insert(),
                [{"user_id": user_id, "role_id": r.id} for r in roles]
            )

        if commit:
            await self.db.commit()
        return roles

    async def disable_users(self, user_ids: List[int], current_user_id: int, disable: bool = True, commit: bool = True):
        """
        Disable or enable a list of users.
        """
        users = await self.repo.get_by_pks(self.db, user_ids)
        for user in users:
            if user.id == current_user_id:
                continue
            user.is_active = not disable if disable else True
            self.db.add(user)

        await self.db.flush()
        if commit:
            await self.db.commit()
        return users
