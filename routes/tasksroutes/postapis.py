from auth import require_roles
from fastapi import APIRouter, Depends
from core.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.task import TaskResponse, TaskCreate
from models.task import Task
from models.user import User

taskRouter = APIRouter(prefix="/api/task")


@taskRouter.post("/create-task", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    user: User = Depends(require_roles("admin", "manager")),
    db: AsyncSession = Depends(async_get_db),
):
    new_task = Task(**task.model_dump(), created_by_id=user.id)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    db.close()
    return new_task
