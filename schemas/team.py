from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List


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



"""Details Model"""

class TeamMemberStats(BaseModel):
    id: UUID
    name: str
    email: str
    task_count: int

    # model_config = ConfigDict(from_attributes=True)
 
 
class ManagerDetails(BaseModel):
    id: UUID
    name: str
    email: str
 
 
class TeamDetailResponse(BaseModel):
    team_id: UUID
    team_name: str
    task_count: int
    member_count: int
    manager: ManagerDetails
    members: List[TeamMemberStats]