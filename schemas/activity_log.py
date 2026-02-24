from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


"""Create Model"""


class ActivityLogCreate(BaseModel):
    user_id: UUID
    action_type: str
    resource_id: UUID


"""Response Model"""


class ActivityLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    action_type: str
    resource_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


"""Update Model"""


class UpdateActivityLog(BaseModel):
    action_type: Optional[str] = None
    resource_id: Optional[UUID] = None
