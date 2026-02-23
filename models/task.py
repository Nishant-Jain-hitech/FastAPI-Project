import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Enum as SQLAlchemyEnum, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from .enums import Priority, Status

if TYPE_CHECKING:
    from .user import User
    from .team import Team


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    priority: Mapped[Priority] = mapped_column(
        SQLAlchemyEnum(Priority), nullable=False, default=Priority.MEDIUM
    )
    status: Mapped[Status] = mapped_column(
        SQLAlchemyEnum(Status), nullable=False, default=Status.TODO
    )

    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="SET NULL"), nullable=True
    )

    created_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    assignee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    is_deleted: Mapped[bool] = mapped_column(default=False)

    team: Mapped["Team"] = relationship("Team", back_populates="tasks")
    creator: Mapped["User"] = relationship(
        "User", foreign_keys="Task.created_by_id", back_populates="created_tasks"
    )
    assignee: Mapped["User"] = relationship(
        "User", foreign_keys="Task.assignee_id", back_populates="assigned_tasks"
    )
