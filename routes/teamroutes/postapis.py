from datetime import datetime
from fastapi import HTTPException
from auth import require_roles
from fastapi import APIRouter, Depends
from core.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession

from models.team import Team, UserTeam
from schemas.team import TeamCreate, TeamResponse
from models.user import User

teamRouter = APIRouter(prefix="/api/team")


@teamRouter.post("/create-team", response_model=TeamResponse)
async def create_task(
    team: TeamCreate,
    user: User = Depends(require_roles("admin", "manager")),
    db: AsyncSession = Depends(async_get_db),
):

    if user.role=="admin" and team.created_by_id is None:
        raise HTTPException(status_code=422, detail="created_by_id daalo bhai")

    if user.role=="admin" and team.created_by_id is not None:
        new_team = Team(name=team.name,created_by_id=team.created_by_id)
        db.add(new_team)
        await db.flush()
        user_team=UserTeam(user_id=team.created_by_id,team_id=new_team.id)

    else:
        new_team = Team(name=team.name,created_by_id=user.id)
        db.add(new_team)
        await db.flush()
        user_team=UserTeam(user_id=user.id,team_id=new_team.id)

    db.add(user_team)
    await db.commit()
    await db.refresh(new_team)
    await db.refresh(user_team)
    db.close()
    return new_team
