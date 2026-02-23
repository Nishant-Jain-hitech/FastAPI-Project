from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class ActivityLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    action_type: str
    resource_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
