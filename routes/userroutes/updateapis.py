from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import async_get_db
from auth import require_roles
from schemas.user import UserResponse, UpdateUser
from models.user import User


userUpdateRouter = APIRouter()


@userUpdateRouter.patch("/update-user", response_model=UserResponse)
async def update_user(
    update_data: UpdateUser,
    current_user: User = Depends(require_roles("admin", "manager", "user")),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(User).where(User.id == update_data.user_id)
    db_result = await db.execute(query)
    target_user = db_result.scalars().first()

    if not target_user:
        raise HTTPException(status_code=404, detail="user nhi h")

    if update_data.role:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="sirf admin role change krega")

        if target_user.role == "admin":
            raise HTTPException(
                status_code=400, detail="admin ka role change nhi karna"
            )

        if target_user.role == update_data.role:
            raise HTTPException(status_code=400, detail="already same role me h")

        if target_user.role == "manager" and update_data.role in ["user", "admin"]:
            raise HTTPException(
                status_code=400, detail=f"manager ko {update_data.role} nhi bana sakte"
            )

        target_user.role = update_data.role

    if update_data.is_active is not None:
        if current_user.role in ["admin", "manager"] and target_user.role != "admin":
            target_user.is_active = update_data.is_active

    if update_data.name and update_data.user_id == current_user.id:
        target_user.name = update_data.name

    try:
        await db.commit()
        await db.refresh(target_user)
        return target_user
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database update failed")
