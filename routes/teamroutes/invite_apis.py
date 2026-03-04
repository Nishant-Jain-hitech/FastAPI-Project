from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jwt
import uuid

from core.database import async_get_db
from core.config import settings
from auth import require_roles
from models.user import User
from models.team import Team, UserTeam
from models.invite_token import InviteToken
from schemas.invite_token import InviteCreate, InviteResponse
from utils.helper import send_invite_email

inviteRouter = APIRouter()


@inviteRouter.post("/create-invite", response_model=InviteResponse)
async def create_invite_token(
    background_task: BackgroundTasks,
    data: InviteCreate,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(require_roles("manager")),
):

    team = await db.get(Team, data.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="The specified team was not found")
    if team.created_by_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Invitations can only be issued for teams you have created",
        )
    query = select(User).where(User.email == data.user_email, User.role == "user")
    result = await db.execute(query)
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User account associated with this email address was not found",
        )
    query = select(UserTeam).where(
        UserTeam.user_id == db_user.id, UserTeam.team_id == data.team_id
    )
    result = await db.execute(query)
    existing_membership = result.scalars().first()
    if existing_membership:
        raise HTTPException(
            status_code=400,
            detail="The specified user is already a member of this team",
        )
    payload = {"sub": data.user_email, "team_id": str(data.team_id)}

    new_token_string = jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    invite = InviteToken(
        team_id=data.team_id,
        created_by_id=current_user.id,
        token=new_token_string,
        expires_at=(datetime.now(timezone.utc) + timedelta(hours=24)).replace(
            tzinfo=None
        ),
    )

    db.add(invite)
    await db.commit()
    await db.refresh(invite)
    background_task.add_task(send_invite_email, data.user_email, new_token_string)
    return invite


@inviteRouter.get("/accept-invite/{token}")
async def accept_invite_token(token: str, db: AsyncSession = Depends(async_get_db)):
    query = select(InviteToken).where(InviteToken.token == token)
    result = await db.execute(query)
    invite = result.scalar_one_or_none()

    if not invite or invite.is_used:
        raise HTTPException(
            status_code=400,
            detail="This invitation link is invalid or has already been used",
        )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        token_team_id = uuid.UUID(payload.get("team_id"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="The invitation link has expired")
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=400, detail="The provided token is malformed or invalid"
        )

    user_query = select(User).where(User.email == email)
    user_result = await db.execute(user_query)
    db_user = user_result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="No user account found matching the invitation criteria",
        )

    user_id_to_add = db_user.id

    new_membership = UserTeam(user_id=user_id_to_add, team_id=token_team_id)

    invite.is_used = True
    db.add(new_membership)

    await db.commit()

    return {"status": "success", "user_id": user_id_to_add, "team_id": token_team_id}
