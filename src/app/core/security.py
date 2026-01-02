import logging
import traceback

from fastapi import Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.core.exceptions import UnauthorizedError
from app.core.jwt import decode_token
from app.core.jwt import verify_token
from app.core.settings import settings
from app.models import User
from app.repositories.iam import UserRepo

REDIS_TTL = 300
user_repo = UserRepo()

logger = logging.getLogger(__name__)


class ServiceOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request):
        try:
            token = await super().__call__(request)
        except HTTPException as e:
            if e.status_code == 401:
                raise UnauthorizedError("Token missing or invalid")
            raise
        return token


oauth2_scheme = ServiceOAuth2PasswordBearer(settings.login_url)

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    deprecated="auto"
)


async def login_required(token: str = Depends(oauth2_scheme)) -> dict:
    payload = verify_token(token)
    if not payload or payload.get("sub") is None:
        raise UnauthorizedError("Token payload missing subject")
    return payload


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Validate token and get user by username.
    Synchronous for simplicity, just returns the ORM object.
    """
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
        # Use UserRepo to get user by username without loading roles/permissions
        user = await user_repo.get_by_pk(db, user_id)
        if not user:
            raise NotFoundError(f"User with ID '{user_id}' not found")
        return user
    except Exception as e:
        logger.debug(traceback.format_exc())
        raise NotFoundError("Invalid token") from e


def has_role(role_name: str):
    async def dependency(
            token: str = Depends(oauth2_scheme),
            db: AsyncSession = Depends(get_db_session),
    ) -> None:
        """
        Verify that the current user has the specified role.
        Loads roles for permission check.
        """
        user_id = int(decode_token(token)["sub"])
        user = await user_repo.get_by_id(db, user_id, load_roles=True)
        if not user:
            raise UnauthorizedError("User not found")

        if role_name not in [r.name for r in user.roles] and not user.is_superuser:
            raise PermissionDeniedError("Insufficient role")
        return

    return dependency


def has_perm(permission_name: str):
    async def dependency(
            token: str = Depends(oauth2_scheme),
            db: AsyncSession = Depends(get_db_session),
    ) -> None:
        """
        Verify that the current user has the specified permission.
        Loads roles and their permissions.
        """
        user_id = int(decode_token(token)["sub"])
        user = await user_repo.get_by_id(db, user_id, load_roles=True, load_permissions=True)
        if not user:
            raise UnauthorizedError("User not found")

        if user.is_superuser:
            return

        user_perms = {p.name for r in user.roles for p in r.permissions}
        if permission_name not in user_perms:
            raise PermissionDeniedError("Insufficient permission")
        return

    return dependency
