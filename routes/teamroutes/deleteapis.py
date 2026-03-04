from auth import require_roles
from logging.config import dictConfig
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_get_db
from models.team import Team
from models.user import User


deleteTeamRouter = APIRouter()


@deleteTeamRouter.delete("/{team_id}", response_model=dict)
async def delete_team(
    team_id: UUID,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    team = (
        await db.execute(
            select(Team).where(
                Team.id == team_id,
                Team.is_deleted == False,
            )
        )
    ).scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=404,
            detail="The specified team could not be found or has already been removed",
        )

    if current_user.role == "admin" or (
        current_user.role == "manager" and team.created_by_id == current_user.id
    ):
        team.is_deleted = True
        await db.commit()
        return {"message": "Team successfully deleted"}

    raise HTTPException(
        status_code=403,
        detail="Access denied: Managers are only permitted to delete teams they have created",
    )
