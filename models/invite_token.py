import uuid
from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

if TYPE_CHECKING:
    from .team import Team


class InviteToken(Base):
    __tablename__ = "invite_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=24)
    )
    is_user: Mapped[bool] = mapped_column(default=False)

    team: Mapped["Team"] = relationship("Team", back_populates="invite_tokens")
