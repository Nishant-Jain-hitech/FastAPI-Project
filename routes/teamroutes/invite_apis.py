import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import async_get_db
from auth import require_roles, get_current_user
from models.user import User
from models.team import Team, UserTeam
from models.invite_token import InviteToken
from schemas.invite_token import InviteCreate, InviteResponse

inviteRouter = APIRouter()


@inviteRouter.post("/create-invite", response_model=InviteResponse)
async def create_invite_token(
    background_task: BackgroundTasks,
    data: InviteCreate,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(require_roles("manager", "admin")),
):
    team = await db.get(Team, data.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if current_user.role == "manager" and team.create_by_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Managers can only invite to their own teams"
        )

    user_query = select(User).where(User.email == data.user_email)
    user_result = await db.execute(user_query)
    target_user = user_result.scalars().first()

    if not target_user:
        raise HTTPException(
            status_code=404, detail="User with this email does not exist"
        )

    token_str = secrets.token_urlsafe(32)
    new_invite = InviteToken(
        team_id=data.team_id,
        created_by_id=current_user.id,
        token=token_str,
        expires_at=(datetime.now(timezone.utc) + timedelta(hours=24)).replace(
            tzinfo=None
        ),
        is_used=False,
    )

    db.add(new_invite)
    await db.commit()
    await db.refresh(new_invite)

    return new_invite


@inviteRouter.post("/accept-invite/{token}")
async def accept_invite(
    token: str,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(InviteToken).where(InviteToken.token == token)
    result = await db.execute(query)
    invite = result.scalar_one_or_none()

    if not invite:
        raise HTTPException(status_code=404, detail="Invalid invitation token")

    if invite.is_used:
        raise HTTPException(status_code=400, detail="This token has already been used")

    # Ensure comparison uses naive datetimes if your DB column is naive
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if invite.expires_at < now:
        raise HTTPException(status_code=400, detail="This invitation has expired")

    membership_check = await db.execute(
        select(UserTeam).where(
            UserTeam.user_id == current_user.id,
            UserTeam.team_id == invite.team_id,
        )
    )

    if membership_check.scalars().first():
        raise HTTPException(
            status_code=400, detail="You are already a member of this team"
        )

    new_membership = UserTeam(user_id=current_user.id, team_id=invite.team_id)

    invite.is_used = True

    await db.add(new_membership)
    await db.commit()

    return {"message": "Successfully joined the team", "team_id": str(invite.team_id)}
