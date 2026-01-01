from sqlalchemy import Column, Integer, Table, ForeignKey

from app.core.db import Base

auth_user_roles = Table(
    "auth_user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("auth_users.id")),
    Column("role_id", Integer, ForeignKey("auth_roles.id"))
)

auth_role_permissions = Table(
    "auth_role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("auth_roles.id")),
    Column("permission_id", Integer, ForeignKey("auth_permissions.id"))
)
