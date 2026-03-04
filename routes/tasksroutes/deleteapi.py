from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_get_db
from models.task import Task

from models.user import User, UserRole
from auth import get_current_user

deleteTaskRouter = APIRouter()


@deleteTaskRouter.delete("/{task_id}", response_model=dict)
async def get_team(
    task_id: UUID,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        await db.execute(
            select(Task).where(
                Task.id == task_id,
                Task.is_deleted == False,
            )
        )
    ).scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="The requested task could not be found or has already been deleted",
        )

    if current_user.role == "admin" or (
        current_user.role == "manager" and task.created_by_id == current_user.id
    ):
        task.is_deleted = True
        await db.commit()
        return {"message": "Task successfully marked as deleted"}

    raise HTTPException(
        status_code=403,
        detail="Access denied: Managers are only permitted to delete tasks they have created",
    )
