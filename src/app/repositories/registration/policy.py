from datetime import datetime, timezone
from typing import Optional

from app.models.registration import InviteCode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepo


class InviteCodeRepo(BaseRepo[InviteCode]):
    model = InviteCode

    def __init__(self):
        super().__init__(InviteCode)

    @classmethod
    async def mark_used(cls, db: AsyncSession, invite: InviteCode, user_id: int):
        invite.used = True
        invite.used_by = user_id
        invite.used_at = datetime.now(timezone.utc)
        db.add(invite)
