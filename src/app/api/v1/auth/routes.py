from fastapi import APIRouter, Depends

from app.api.v1.auth.deps import get_user_service
from app.api.v1.auth.schemas import UserOut, UserLogin, TokenOut, TokenRefresh, UserRegister, get_password_rules
from app.core.jwt import create_access_token, create_refresh_token
from app.schemas.response import Response
from app.services.auth import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Response[UserOut])
async def register(
        data: UserRegister,
        service: UserService = Depends(get_user_service)
):
    user = await service.register_user(data)
    return Response(data=UserOut.model_validate(user))


@router.post("/login", response_model=Response[TokenOut])
async def login(
        data: UserLogin,
        service: UserService = Depends(get_user_service)
):
    tokens = await service.login(data.username, data.password)
    data = TokenOut(**tokens).model_dump()
    return Response(data=data)


@router.post("/refresh", response_model=Response[TokenOut])
async def refresh(
        data: TokenRefresh,
        service: UserService = Depends(get_user_service)
):
    return Response(data=TokenOut(**await service.refresh_token(data.refresh_token)))


@router.get("/password-rules")
async def password_rules():
    return Response(data=get_password_rules())
