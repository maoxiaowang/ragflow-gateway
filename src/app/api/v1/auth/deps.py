from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.exceptions import NotFoundError
from app.core.jwt import decode_token
from app.core.security import oauth2_scheme
from app.models.auth import User
from app.services.auth import UserService


def get_user_service(db: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(db)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)):
    """
    验证token有效性，并获取用户对象
    """
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise NotFoundError(f"User '{username}' not found")
        return user
    except Exception as e:
        # 其它解码异常可以用自定义异常
        raise NotFoundError("Invalid token") from e


def has_role(role_name: str):
    def dependency(user: User = Depends(get_current_user)):
        if user.is_superuser:  # 超级管理员默认通过
            return user
        if role_name not in [r.name for r in user.roles]:
            raise NotFoundError("Insufficient role")
        return user
    return dependency


def has_perm(permission_name: str):
    def dependency(user: User = Depends(get_current_user)):
        if user.is_superuser:
            return user
        permissions = {p.name for r in user.roles for p in r.permissions}
        if permission_name not in permissions:
            raise NotFoundError("Insufficient permission")
        return user
    return dependency
