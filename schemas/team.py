from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


"""Create Model"""


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    created_by_id: Optional[UUID]=None


class UserTeamCreate(BaseModel):
    user_id: UUID
    team_id: UUID


"""Response Model"""


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


"""Update Model"""


class UpdateTeam(BaseModel):
    team_id:UUID
    name: Optional[str]
