from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.models.iam.through import auth_role_permissions
from app.models.mixin import TimestampMixin


class Permission(TimestampMixin, Base):
    __tablename__ = "auth_permissions"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    roles = relationship("Role", secondary=auth_role_permissions, back_populates="permissions")
