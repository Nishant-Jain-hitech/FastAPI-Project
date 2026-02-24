from fastapi import HTTPException
from sqlalchemy import UUID
from auth import require_roles
from fastapi import APIRouter, Depends
from core.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas.user import UserResponse
from models.user import User


userGetRouter = APIRouter()


@userGetRouter.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(require_roles("admin", "manager", "user")),
    db: AsyncSession = Depends(async_get_db),
):
    return user


@userGetRouter.get("/all", response_model=list[UserResponse])
async def get_all_users(
    user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(User)
    result = await db.execute(query)
    result = result.scalars().all()
    db.close()
    return result


@userGetRouter.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    user: User = Depends(require_roles("admin", "manager")),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    result = result.scalars().first()

    if not result:
        raise HTTPException(status_code=404, detail="user nhi h")
