"""
API-V1路由聚合
"""
from fastapi import APIRouter

from app.api.v1.auth.routes import router as auth_router
from app.api.v1.user.routes import router as user_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth_router)
v1_router.include_router(user_router)