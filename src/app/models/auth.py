from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship

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


class User(Base):
    __tablename__ = "auth_users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    roles = relationship("Role", secondary=auth_user_roles, back_populates="users")


class Role(Base):
    __tablename__ = "auth_roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    permissions = relationship("Permission", secondary=auth_role_permissions, back_populates="roles")
    users = relationship("User", secondary=auth_user_roles, back_populates="roles")


class Permission(Base):
    __tablename__ = "auth_permissions"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    roles = relationship("Role", secondary=auth_role_permissions, back_populates="permissions")
