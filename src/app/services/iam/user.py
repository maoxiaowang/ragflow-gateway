from typing import List, Optional

from app.core.exceptions import ConflictError
from app.core.security import pwd_context
from app.models import User, Role
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

    async def create(self, data, commit=True, roles: Optional[List[Role]] = None):
        roles = roles or []
        await self.check_before_create(data)
        username = data["username"]
        hashed_password = pwd_context.hash(data["password"])
        user = await self.repo.create_user(
            self.db, username=username, password=hashed_password, roles=roles
        )
        return user
