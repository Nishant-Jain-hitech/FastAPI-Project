from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database import async_get_db
from auth import get_current_user
from models.task import Task
from models.enums import Status
from models.user import User
from models.team import Team, UserTeam


getTaskRouter = APIRouter()



@getTaskRouter.get("/stats")
async def get_task_stats(
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),
):
    base_query = select(Task.status, func.count(Task.id)).where(
        Task.is_deleted == False
    )
 
    if current_user.role == "admin":
        query = base_query.group_by(Task.status)
 
    elif current_user.role == "manager":
        subquery = select(Team.id).where(
            Team.created_by_id == current_user.id,
            Team.is_deleted == False,
        )
 
        query = (
            base_query
            .where(Task.team_id.in_(subquery))
            .group_by(Task.status)
        )
 
    else:
        subquery = select(UserTeam.team_id).where(
            UserTeam.user_id == current_user.id
        )
 
        query = (
            base_query
            .where(Task.team_id.in_(subquery))
            .group_by(Task.status)
        )
 
    result = await db.execute(query)
    rows = result.all()
 
    stats = {status.name: 0 for status in Status}
 
    for status, count in rows:
        stats[status.name] = count
 
    return stats