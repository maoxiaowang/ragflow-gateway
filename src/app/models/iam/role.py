from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.models.iam.through import auth_role_permissions, auth_user_roles
from app.models.mixin import TimestampMixin


class Role(TimestampMixin, Base):
    __tablename__ = "auth_roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    display_name = Column(String)

    permissions = relationship("Permission", secondary=auth_role_permissions, back_populates="roles")
    users = relationship("User", secondary=auth_user_roles, back_populates="roles")
