from fastapi import APIRouter, Depends

from app.api.v1.auth.deps import get_registration_service, get_login_service
from app.core.validators.password import get_password_rules
from app.schemas.auth import UserLogin, TokenOut, TokenRefresh, UserRegister
from app.schemas.iam import UserOut
from app.schemas.response import Response
from app.services.auth import LoginService
from app.services.auth.registration import RegistrationService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Response[UserOut])
async def register(
        data: UserRegister,
        service: RegistrationService = Depends(get_registration_service)
):
    user = await service.register_user(data)
    return Response(data=UserOut.model_validate(user))


@router.post("/login", response_model=Response[TokenOut])
async def login(
        data: UserLogin,
        service: LoginService = Depends(get_login_service)
):
    tokens = await service.login(data.username, data.password)
    data = TokenOut(**tokens).model_dump()
    return Response(data=data)


@router.post("/refresh", response_model=Response[TokenOut])
async def refresh(
        data: TokenRefresh,
        service: LoginService = Depends(get_login_service)
):
    return Response(data=TokenOut(**await service.refresh_token(data.refresh_token)))


@router.get("/password-rules")
async def password_rules():
    return Response(data=get_password_rules())
