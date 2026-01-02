from typing import List

from pydantic import BaseModel

from app.schemas.iam.permissions import PermissionOut


class RoleOut(BaseModel):
    id: int
    name: str
    permissions: List[PermissionOut] = []
