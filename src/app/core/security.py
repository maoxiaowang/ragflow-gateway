from fastapi import Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import UnauthorizedError
from app.core.jwt import verify_token
from app.core.settings import settings


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


async def login_required(token: str = Depends(oauth2_scheme)) -> dict:
    """
    验证 token
    """
    payload = verify_token(token)
    if not payload or payload.get("sub") is None:
        raise UnauthorizedError("Token payload missing subject")
    return payload
