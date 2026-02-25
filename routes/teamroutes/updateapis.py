from sqlalchemy import select
from fastapi import HTTPException
from auth import require_roles
from fastapi import APIRouter, Depends
from core.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession

from models.team import Team
from schemas.team import TeamResponse, UpdateTeam
from models.user import User

teamUpdateRouter = APIRouter()


@teamUpdateRouter.patch("/update-team", response_model=TeamResponse)
async def update_team(
    team_data: UpdateTeam,
    user: User = Depends(require_roles("admin", "manager")),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(Team).where(Team.id == team_data.team_id)
    existing_record = await db.execute(query)
    existing_record = existing_record.scalars().first()

    if not existing_record:
        raise HTTPException(status_code=404, detail="team nhi h")

    if user.role == "manager" and existing_record.created_by_id != user.id:
        raise HTTPException(
            status_code=403, detail="apna team dekho bhai, dusre me nhi aana"
        )

    existing_record.name = team_data.name
    await db.commit()
    await db.refresh(existing_record)
    db.close()
    return existing_record
