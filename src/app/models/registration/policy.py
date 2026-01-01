from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from app.core.db import Base
from app.models.mixin import TimestampMixin


class InviteCode(TimestampMixin, Base):
    __tablename__ = "auth_invite_codes"

    code = Column(String, primary_key=True, index=True)
    used = Column(Boolean, default=False)
    used_by = Column(Integer, ForeignKey("auth_users.id"), nullable=True, index=True)
