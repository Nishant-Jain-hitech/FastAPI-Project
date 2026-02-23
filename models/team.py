import uuid
from typing import TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base


if TYPE_CHECKING:
    from .user import User
    from .task import Task
    from .invite_token import InviteToken


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    name: Mapped[str] = mapped_column(nullable=False)

    created_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    is_deleted: Mapped[bool] = mapped_column(default=False)

    user_team: Mapped[list["UserTeam"]] = relationship(
        "UserTeam", back_populates="team"
    )

    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="team", cascade="all,delete-orphan"
    )

    invite_tokens: Mapped[list["InviteToken"]] = relationship(
        "InviteToken", back_populates="team", cascade="all,delete-orphan"
    )


class UserTeam(Base):
    __tablename__ = "user_teams"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )

    joined_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="user_team")
    team: Mapped["Team"] = relationship("Team", back_populates="user_team")
