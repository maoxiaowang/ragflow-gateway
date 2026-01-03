from datetime import datetime, UTC

from pydantic import computed_field
from sqlalchemy import Column, DateTime, func


class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    @computed_field
    @property
    def updated_at(self) -> datetime:
        """
        Return the 'updated_at' value safely without triggering lazy loading.

        - If 'updated_at' has been explicitly set or loaded, return it.
        - Otherwise, return a fallback value (e.g., current UTC time).

        This avoids SQLAlchemy lazy-loading errors (MissingGreenlet) when
        serializing the model for responses, and ensures a valid datetime
        is always returned.
        """
        return self.__dict__.get("updated_at", datetime.now(UTC))
