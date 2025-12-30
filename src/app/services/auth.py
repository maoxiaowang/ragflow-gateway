import string
from datetime import timedelta
from secrets import choice
from typing import List

from app.api.v1.auth.schemas import UserCreate, UserRegister
from app.core.exceptions import UnauthorizedError, ConflictError
from app.core.jwt import create_access_token, create_refresh_token, verify_token
from app.core.settings import settings
from app.models.auth import User, InviteCode
from app.repositories.auth import UserRepo, InviteCodeRepo, RoleRepo
from app.services.base import BaseService


class UserService(BaseService[User]):
    repo = UserRepo()
    role_repo = RoleRepo()
    invite_code_repo = InviteCodeRepo()
    model = User

    async def check_before_create(self, data: dict):
        username = data.get("username")
        if username:
            user = await self.repo.get_by_username(self.db, username)
            if user:
                raise ConflictError(f"Username '{username}' already exists")

    async def validate_invite_code(self, code: str) -> InviteCode:
        invite = await InviteCodeRepo().get_by_code(self.db, code)
        if not invite:
            raise ConflictError("邀请码不存在")
        if invite.used:
            raise ConflictError("邀请码已被使用")
        return invite

    async def register_user(self, data: UserRegister) -> User:
        # 校验用户名和密码
        await self.check_before_create({"username": data.username})

        # 校验邀请码
        invite = await self.validate_invite_code(data.invite_code)

        # 创建用户并分配默认角色
        default_role = await self.role_repo.get_or_create(self.db, "user")
        user_data = UserCreate(username=data.username, password=data.password1)
        user = await self.repo.create_user(
            db=self.db,
            username=user_data.username,
            password=user_data.password,
            roles=[default_role],
        )

        # 标记邀请码已用
        await InviteCodeRepo.mark_used(self.db, invite, user.id)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def authenticate(self, username: str, password: str) -> User | None:
        user = await self.repo.authenticate(self.db, username, password)
        if not user:
            raise UnauthorizedError()
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
        access_token = create_access_token(user_id, timedelta(days=settings.refresh_token_expire_days))
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def generate_invite_code(length: int = 12) -> str:
        """生成安全随机邀请码"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(choice(chars) for _ in range(length))

    async def create_invite_codes(self, count: int, length: int = 12, commit=True) -> List[InviteCode]:
        """批量生成邀请码"""
        codes: List[InviteCode] = []
        while len(codes) < count:
            code = self.generate_invite_code(length)
            exists = await self.invite_code_repo.get_by_code(self.db, code)
            if not exists:
                codes.append(InviteCode(code=code))
        return await self.invite_code_repo.bulk_create(self.db, codes, commit=commit)
