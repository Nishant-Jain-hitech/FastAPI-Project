from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from auth import require_roles
from fastapi import APIRouter, Depends
from core.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession

from models.team import Team, UserTeam
from schemas.team import TeamResponse
from models.user import User


teamGetRouter = APIRouter()


@teamGetRouter.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: UUID,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(require_roles("admin", "manager", "user")),
):
    team = (
        (
            await db.execute(
                select(Team).where(
                    Team.id == team_id,
                    Team.is_deleted == False,
                )
            )
        )
        .scalars()
        .first()
    )

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if current_user.role == "admin":
        return team

    if current_user.role == "manager":
        if team.created_by_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="apna team dekho",
            )
        return team

    membership = (
        await db.execute(
            select(UserTeam).where(
                UserTeam.team_id == team_id,
                UserTeam.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="is team me nhi h aap",
        )

    return team
