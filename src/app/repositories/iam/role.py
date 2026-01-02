from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Role
from app.repositories.base import BaseRepo


class RoleRepo(BaseRepo[Role]):
    model = Role
