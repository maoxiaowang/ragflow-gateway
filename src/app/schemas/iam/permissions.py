from pydantic import BaseModel


class PermissionOut(BaseModel):
    id: int
    name: str
