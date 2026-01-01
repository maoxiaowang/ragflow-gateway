from sqlalchemy import Column, Integer, String, Boolean
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
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    roles = relationship("Role", secondary=auth_user_roles, back_populates="users")

    dataset_relations = relationship("RagflowDatasetUser", back_populates="user")
    document_relations = relationship("RagflowDocumentUser", back_populates="user")
