from app.models import Role
from app.repositories.iam import RoleRepo
from app.services.base import BaseService


class RoleService(BaseService[Role]):
    model = Role
    repo = RoleRepo
