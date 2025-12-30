from datetime import datetime, timezone

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey, Index
from sqlalchemy.sql.sqltypes import Integer, String, DateTime, Enum

from app.core.db import Base
from app.models.mixin import TimestampMixin


class RagflowDatasetUser(TimestampMixin, Base):
    __tablename__ = "ragflow_dataset_user"
    __table_args__ = (
        Index("idx_user_dataset", "user_id", "dataset_id"),
    )

    id = Column(Integer, primary_key=True)
    dataset_id = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("auth_users.id"), nullable=False)

    role = Column(Enum("owner", "editor", "viewer", name="dataset_user_role"), default="owner")  # owner / editor / viewer
    user = relationship("User", back_populates="dataset_relations")


class RagflowDocumentUser(TimestampMixin, Base):
    __tablename__ = "ragflow_document_user"
    __table_args__ = (
        Index("idx_user_document", "user_id", "document_id"),
    )

    id = Column(Integer, primary_key=True)
    document_id = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("auth_users.id"), nullable=False)

    user = relationship("User", back_populates="document_relations")
