from pydantic import BaseModel, ConfigDict, Field, field_validator
from uuid import UUID
from typing import Optional, List
from .enums import Priority, Status

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: Status = Status.TODO

    @field_validator("title")
    def sanitize_title(cls, v: str) -> str:
        cleaned = v.capitalize()
        if not cleaned:
            raise ValueError("Title cannot be empty strings")
        return cleaned

class TaskCreate(TaskBase):
    team_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None


class TaskBulkCreate(BaseModel):
    tasks: List[TaskCreate] = Field(..., min_length=1)

    @field_validator("tasks")
    def check_max_batch_size(cls, v: List[TaskCreate]) -> List[TaskCreate]:
        if len(v) > 50:
            raise ValueError("Bulk create limit is 50 tasks per request")
        return v

class TaskStats(BaseModel):
    todo: int
    doing: int
    done: int
    total: int


class TaskResponse(TaskBase):
    id: UUID
    team_id: Optional[UUID]
    created_by_id: UUID
    assignee_id: Optional[UUID]
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)