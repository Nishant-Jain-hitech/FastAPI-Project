from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


from models.activity_log import ActivityLog
from models.user import User
from models.team import UserTeam
from schemas.activity_log import ActivityLogResponse
from core.database import async_get_db
from auth import get_current_user

activityRouter = APIRouter()


@activityRouter.get("/", response_model=List[ActivityLogResponse])
async def get_activity_logs(
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
):
    query = select(ActivityLog).order_by(ActivityLog.timestamp.desc())

    if current_user.role != "admin":
        user_teams_subquery = (
            select(UserTeam.team_id).where(UserTeam.user_id == current_user.id)
        ).scalar_subquery()

        teammate_ids_subquery = (
            select(UserTeam.user_id).where(UserTeam.team_id.in_(user_teams_subquery))
        ).scalar_subquery()

        query = query.where(ActivityLog.user_id.in_(teammate_ids_subquery))

    result = await db.execute(query.limit(limit).offset(offset))
    return result.scalars().all()
