from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.models.iam.through import auth_user_roles
from app.models.mixin import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "auth_users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    nickname = Column(String)
    avatar = Column(String)
    password = Column(String)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    last_login_at = Column(DateTime(timezone=True), default=None)
    email  = Column(String(64), unique=True, index=True, nullable=True)
    mobile = Column(String(32), unique=True, index=True, nullable=True)

    roles = relationship("Role", secondary=auth_user_roles, back_populates="users")

    dataset_relations = relationship("RagflowDatasetUser", back_populates="user")
    document_relations = relationship("RagflowDocumentUser", back_populates="user")
