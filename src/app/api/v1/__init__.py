"""
API-V1路由聚合
"""
from fastapi import APIRouter

from app.api.v1.auth.routes import router as auth_router
from app.api.v1.author.routes import router as authors_router
from app.api.v1.book.routes import router as books_router
from app.api.v1.category.routes import router as categories_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(books_router)
v1_router.include_router(authors_router)
v1_router.include_router(categories_router)
v1_router.include_router(auth_router)
