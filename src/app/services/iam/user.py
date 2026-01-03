import secrets
import string
from typing import List, Optional, Dict

from sqlalchemy.orm import selectinload

from app.api.v1.iam.schemas import CreateUserRequest
from app.core.exceptions import ConflictError, NotFoundError, ServiceValidationError
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

        password = data.get("password")
        if not password:
            raise ValueError("Password cannot be empty")

    async def create_user(
            self,
            data: dict | CreateUserRequest,
            roles: Optional[List[Role]] = None,
            commit: bool = True
    ) -> User:
        """
        Create a user from the admin view.
        """
        user = await super().create(data=data, commit=False)

        attrs = self._prepare_create_data(data)
        password = attrs["password"]
        hashed_password = pwd_context.hash(password)
        user.password = hashed_password

        roles = roles or []
        user.roles = roles

        self.db.add(user)
        if commit:
            await self.db.commit()
            await self.db.refresh(user)

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
                raise ServiceValidationError("Cannot disable your own account.")
            if user.is_superuser:
                raise ServiceValidationError("Cannot disable superuser accounts.")
            user.is_active = not disable
            self.db.add(user)

        await self.db.flush()
        if commit:
            await self.db.commit()
        return users

    # async def reset_password(
    #         self,
    #         *,
    #         user_id: int,
    #         current_user_id: int | None = None,
    #         commit: bool = True,
    #         generate_random: bool = True,
    #         new_password: str | None = None,
    # ) -> str:
    #     """
    #     Reset a user's password.
    #
    #     - current_user_id: the id of the admin performing the reset
    #     - generate_random: if True, a random password is generated
    #     - new_password: if provided, will use this password instead of generating
    #
    #     Returns the new password (plain text) so it can be shown / emailed.
    #     """
    #     if current_user_id and user_id == current_user_id:
    #         raise ServiceValidationError("Cannot reset your own password, use change password instead.")
    #
    #     user = await self.repo.get_by_pk(self.db, user_id)
    #     if not user:
    #         raise NotFoundError(f"User with ID {user_id} not found")
    #
    #     if generate_random:
    #         alphabet = string.ascii_letters + string.digits
    #         new_password = ''.join(secrets.choice(alphabet) for _ in range(12))
    #     elif not new_password:
    #         raise ValueError("Must provide a new password if not generating randomly")
    #
    #     user.password = pwd_context.hash(new_password)
    #     self.db.add(user)
    #
    #     if commit:
    #         await self.db.commit()
    #         await self.db.refresh(user)
    #
    #     return new_password

    async def delete_users_batch(
            self,
            user_ids: List[int],
            current_user_id: int,
            commit: bool = True,
    ) -> List[Dict]:
        """
        Batch delete users.
        """
        results = []

        # Exclude the current user from deletion
        ids_to_delete = [uid for uid in user_ids if uid != current_user_id]

        users = await self.repo.get_by_pks(self.db, user_ids)
        existing_ids = {u.id for u in users}

        for uid in user_ids:
            if uid == current_user_id:
                results.append({"id": uid, "success": False, "reason": "Cannot delete yourself"})
            elif uid not in existing_ids:
                results.append({"id": uid, "success": False, "reason": "User not found"})
            else:
                results.append({"id": uid, "success": True, "reason": None})

        await self.repo.delete_batch(self.db, ids_to_delete)

        if commit:
            await self.db.commit()
        return results

    async def delete_user(
            self,
            user_id: int,
            current_user_id: int,
            commit: bool = True,
    ) -> Dict:
        """
        Delete a single user by reusing the batch deletion logic.
        """
        results = await self.delete_users_batch([user_id], current_user_id, commit)
        return results[0]
