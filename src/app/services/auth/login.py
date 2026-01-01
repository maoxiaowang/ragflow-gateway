from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.jwt import create_access_token, create_refresh_token, verify_token
from app.core.security import pwd_context
from app.core.settings import settings
from app.models import User
from app.repositories.iam import UserRepo
from app.services.base import BaseService


class LoginService(BaseService[User]):
    repo = UserRepo()
    model = User

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def authenticate(self, db: AsyncSession, username: str, password: str) -> User | None:
        user = await self.repo.get_by_username(db, username)
        if user and self.verify_password(password, user.hashed_password):
            return user
        return None

    async def login(self, username: str, password: str) -> dict[str, str]:
        user = await self.authenticate(self.db, username, password)
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    @staticmethod
    async def refresh_token(refresh_token: str) -> dict[str, str]:
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Token invalid or expired")
        user_id = payload["sub"]
        access_token = create_access_token(user_id, timedelta(days=settings.refresh_token_expire_days))
        return {"access_token": access_token, "token_type": "bearer"}
