from models.enums import UserRole
from auth import get_current_user
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from auth import require_roles
from fastapi import APIRouter, Depends
from core.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession

from models.team import Team, UserTeam
from schemas.team import (
    TeamResponse,
    TeamDetailResponse,
    TeamMemberStats,
    ManagerDetails,
)
from models.user import User
from models.task import Task
from sqlalchemy import func


teamGetRouter = APIRouter()


@teamGetRouter.get("/all-teams", response_model=list[TeamResponse])
async def list_teams(
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
        teams = (
            (await db.execute(select(Team).where(Team.is_deleted.is_(False))))
            .scalars()
            .all()
        )
        return teams

    if current_user.role == "manager":
        teams = (
            (
                await db.execute(
                    select(Team).where(
                        Team.created_by_id == current_user.id,
                        Team.is_deleted.is_(False),
                    )
                )
            )
            .scalars()
            .all()
        )
        return teams

    teams = (
        (
            await db.execute(
                select(Team)
                .join(UserTeam, Team.id == UserTeam.team_id)
                .where(
                    UserTeam.user_id == current_user.id,
                    Team.is_deleted.is_(False),
                )
            )
        )
        .scalars()
        .all()
    )

    return teams


@teamGetRouter.get("/{team_id}", response_model=TeamDetailResponse)
async def get_team_details(
    team_id: UUID,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),
):
    team = (
        await db.execute(
            select(Team).where(
                Team.id == team_id,
                Team.is_deleted.is_(False),
            )
        )
    ).scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=404,
            detail="The requested team does not exist or has been deleted",
        )

    if current_user.role == UserRole.ADMIN:
        pass

    elif current_user.role == UserRole.MANAGER:
        if team.created_by_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: You do not have permission to view this team's details",
            )
    else:
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
                detail="Access denied: You are not a member of this team",
            )

    task_count = (
        await db.execute(
            select(func.count(Task.id)).where(
                Task.team_id == team_id,
                Task.is_deleted.is_(False),
            )
        )
    ).scalar()

    member_count = (
        await db.execute(
            select(func.count(UserTeam.user_id)).where(
                UserTeam.team_id == team_id,
            )
        )
    ).scalar()

    manager = (
        await db.execute(select(User).where(User.id == team.created_by_id))
    ).scalar_one()

    members = (
        (
            await db.execute(
                select(User)
                .join(UserTeam, User.id == UserTeam.user_id)
                .where(UserTeam.team_id == team_id)
            )
        )
        .scalars()
        .all()
    )

    members_data = []

    for member in members:
        user_task_count = (
            await db.execute(
                select(func.count(Task.id)).where(
                    Task.assignee_id == member.id,
                    Task.team_id == team_id,
                    Task.is_deleted.is_(False),
                )
            )
        ).scalar()

        members_data.append(
            TeamMemberStats(
                id=member.id,
                name=member.name,
                email=member.email,
                task_count=user_task_count,
            )
        )

    return TeamDetailResponse(
        team_id=team.id,
        team_name=team.name,
        task_count=task_count,
        member_count=member_count,
        manager=ManagerDetails(
            id=manager.id,
            name=manager.name,
            email=manager.email,
        ),
        members=members_data,
    )
