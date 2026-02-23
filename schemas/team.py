from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    pass


class TeamResponse(TeamBase):
    id: UUID
    created_by_id: UUID
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class UserTeamResponse(BaseModel):
    user_id: UUID
    team_id: UUID
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
