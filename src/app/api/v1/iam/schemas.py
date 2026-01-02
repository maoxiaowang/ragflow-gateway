from typing import List, Optional

from pydantic import BaseModel


class AssignRolesRequest(BaseModel):
    role_ids: List[int]


class CreateUserRequest(BaseModel):
    username: str
    password: str
    nickname: Optional[str]
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class DisableUsersRequest(BaseModel):
    user_ids: List[int]
    disable: bool = True
