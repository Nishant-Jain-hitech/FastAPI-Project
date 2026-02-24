from auth import require_roles
from fastapi import APIRouter, Depends, HTTPException
from core.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import schemas
from schemas.team import UserTeamResponse, UserTeamCreate
from models.user import User
from models.team import UserTeam, Team
from auth import hash_password, verify_password, create_access_token

userRouter = APIRouter(prefix="/api/user")


@userRouter.post("/signup", response_model=schemas.user.UserResponse | dict)
async def create_user(
    user: schemas.user.UserCreate,
    current_user: User = Depends(require_roles("admin", "manager")),
    db: AsyncSession = Depends(async_get_db),
):
    if current_user.role == "manager" and user.role in ["admin", "manager"]:
        raise HTTPException(
            status_code=403, detail="manager admin/manager nhi bna sakta"
        )
    hashed_password = hash_password(user.password)
    db_user = User(
        name=user.name, email=user.email, password=hashed_password, role=user.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    db.close()

    return db_user


@userRouter.post("/login", response_model=schemas.user.UserLoginResponse)
async def login(user: schemas.user.UserLogin, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(status_code=404, detail="bhai user nhi h, email check kar")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.email})

    return {"access_token": access_token}


@userRouter.post("/assign-team", response_model=UserTeamResponse)
async def assign_team(
    user_team: UserTeamCreate,
    user: User = Depends(require_roles("manager")),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(UserTeam).where(
        UserTeam.user_id == user_team.user_id, UserTeam.team_id == user_team.team_id
    )
    result = await db.execute(query)
    existing_record = result.scalars().first()
    if existing_record:
        raise HTTPException(status_code=400, detail="user pehle se team me h")

    db_user = await db.execute(select(User).where(User.id == user_team.user_id))
    db_user = db_user.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="user nhi h")

    db_team = await db.execute(select(Team).where(Team.id == user_team.team_id))
    db_team = db_team.scalars().first()
    if not db_team:
        raise HTTPException(status_code=404, detail="team nhi h")

    if user_team.created_by_id!=user.id:
        raise HTTPException(status_code=403, detail="apna team dekho bhai, dusre me nhi aana")

    user_team = UserTeam(user_id=user_team.user_id, team_id=user_team.team_id)
    db.add(user_team)
    await db.commit()
    await db.refresh(user_team)
    db.close()
    return user_team
