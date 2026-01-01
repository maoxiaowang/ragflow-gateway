from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.services.iam import UserService
from app.services.iam.permission import PermissionService
from app.services.iam.role import RoleService


def get_user_service(db: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(db)


def get_role_service(db: AsyncSession = Depends(get_db_session)) -> RoleService:
    return RoleService(db)


def get_permission_service(db: AsyncSession) -> PermissionService:
    return PermissionService(db)
