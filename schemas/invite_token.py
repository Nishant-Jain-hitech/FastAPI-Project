from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class InviteCreate(BaseModel):
    team_id: UUID
    is_used: bool = False


class InviteResponse(BaseModel):
    id: UUID
    team_id: UUID
    created_by_id: UUID
    expires_at: datetime
    is_used: bool

    model_config = ConfigDict(from_attributes=True)
