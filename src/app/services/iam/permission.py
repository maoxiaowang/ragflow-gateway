from app.models import Permission
from app.repositories.iam import PermissionRepo
from app.services.base import BaseService


class PermissionService(BaseService[Permission]):
    model = Permission
    repo = PermissionRepo
