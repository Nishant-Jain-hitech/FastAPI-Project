import uuid
from typing import TYPE_CHECKING
from sqlalchemy import UUID, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from .enums import UserRole


if TYPE_CHECKING:
    from .team import UserTeam
    from .task import Task
    from .activity_log import ActivityLog


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    user_team: Mapped[list["UserTeam"]] = relationship(
        "UserTeam", back_populates="user"
    )

    created_tasks: Mapped[list["Task"]] = relationship(
        "Task", foreign_keys="Task.created_by_id", back_populates="creator"
    )
    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task", foreign_keys="Task.assignee_id", back_populates="assignee"
    )

    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog", back_populates="user"
    )
