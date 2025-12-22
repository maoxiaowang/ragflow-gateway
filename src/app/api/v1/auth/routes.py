from fastapi import APIRouter, Depends

from app.api.v1.auth.deps import get_user_service
from app.api.v1.auth.schemas import UserOut, UserLogin, TokenOut, TokenRefresh, UserRegister
from app.core.jwt import create_access_token, create_refresh_token
from app.schemas.response import Response
from app.services.auth import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Response[UserOut])
async def register(
        data: UserRegister,
        s: UserService = Depends(get_user_service)
):
    user = await s.register_user(data)
    return Response(data=UserOut.model_validate(user))


@router.post("/login", response_model=Response[TokenOut])
async def login(
        data: UserLogin,
        s: UserService = Depends(get_user_service)
):
    user = await s.authenticate(data.username, data.password)
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    data = TokenOut(
        access_token=access_token,
        refresh_token=refresh_token
    ).model_dump()
    return Response(data=data)


@router.post("/refresh", response_model=Response[TokenOut])
async def refresh(
        data: TokenRefresh,
        s: UserService = Depends(get_user_service)
):
    return Response(data=TokenOut(**await s.refresh_token(data.refresh_token)))
