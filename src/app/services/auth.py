from app.api.v1.auth.schemas import UserCreate
from app.core.exceptions import UnauthorizedError, ConflictError
from app.core.jwt import create_access_token, create_refresh_token, verify_token
from app.models.auth import User
from app.repositories.auth import UserRepo
from app.services.base import BaseService


class UserService(BaseService[User]):
    repo = UserRepo()
    model = User

    async def check_before_create(self, data: dict):
        username = data.get("username")
        if username:
            user = await self.repo.get_by_username(self.db, username)
            if user:
                raise ConflictError(f"Username '{username}' already exists")

    async def create_user(self, data: UserCreate) -> User:
        await self.check_before_create(data.model_dump())

        hashed_password = self.repo.get_password_hash(data.password)
        user = User(username=data.username, hashed_password=hashed_password)

        await self.repo.create(self.db, user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate(self, username: str, password: str) -> User | None:
        user = await self.repo.authenticate(self.db, username, password)
        if not user:
            raise UnauthorizedError
        return user

    async def login(self, username: str, password: str) -> dict[str, str]:
        user = await self.authenticate(username, password)
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    @staticmethod
    async def refresh_token(refresh_token: str) -> dict[str, str]:
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Token invalid or expired")
        user_id = payload["sub"]
        # 扩展操作，可以在这里检查用户是否被禁用
        access_token = create_access_token(user_id)
        return {"access_token": access_token, "token_type": "bearer"}
