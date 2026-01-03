import string
from secrets import choice
from typing import List

from app.constants.roles import SystemRoles
from app.core.exceptions import ConflictError
from app.models import User, InviteCode
from app.repositories.iam import UserRepo, RoleRepo
from app.repositories.registration import InviteCodeRepo
from app.schemas.auth import UserRegister
from app.schemas.iam import UserCreate
from app.services.base import BaseService


class RegistrationService(BaseService[User]):
    repo = UserRepo()
    role_repo = RoleRepo()
    invite_code_repo = InviteCodeRepo()
    model = User

    async def validate_invite_code(self, code: str) -> InviteCode:
        invite = await self.invite_code_repo.get_by_pk(self.db, code)
        if not invite:
            raise ConflictError("邀请码不存在")
        if invite.used:
            raise ConflictError("邀请码已被使用")
        return invite

    @staticmethod
    def generate_invite_code(length: int = 12) -> str:
        chars = string.ascii_uppercase + string.digits
        return ''.join(choice(chars) for _ in range(length))

    async def create_invite_codes(self, count: int, length: int = 12) -> List[InviteCode]:
        codes: List[InviteCode] = []
        while len(codes) < count:
            code = self.generate_invite_code(length)
            exists = await self.invite_code_repo.get_by_pk(self.db, code)
            if not exists:
                codes.append(InviteCode(code=code))
        objs = await self.invite_code_repo.bulk_create(self.db, codes)
        await self.db.commit()
        return objs

    async def register_user(self, data: UserRegister) -> User:
        await self.check_before_create({"username": data.username})
        invite = await self.validate_invite_code(data.invite_code)

        # Create user and assign default role
        user_data = UserCreate(username=data.username, password=data.password1)
        default_role, created = await self.role_repo.get_or_create(
            self.db, field_name="name", value=SystemRoles.DEFAULT
        )
        user = await self.repo.create_user(
            db=self.db,
            username=user_data.username,
            password=user_data.password,
            roles=[default_role],
        )

        await InviteCodeRepo.mark_used(self.db, invite, user.id)

        await self.db.commit()
        await self.db.refresh(user)
        return user
