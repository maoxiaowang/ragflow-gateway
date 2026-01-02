from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.services.auth import LoginService
from app.services.auth.registration import RegistrationService


def get_registration_service(db: AsyncSession = Depends(get_db_session)) -> RegistrationService:
    return RegistrationService(db)


def get_login_service(db: AsyncSession = Depends(get_db_session)) -> LoginService:
    return LoginService(db)
