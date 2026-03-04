from auth import require_roles
from fastapi import APIRouter, Depends
from core.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.task import TaskResponse, TaskCreate
from models.task import Task
from models.user import User
from models.activity_log import ActivityLog

taskRouter = APIRouter()


@taskRouter.post("/create-task", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    user: User = Depends(require_roles("admin", "manager")),
    db: AsyncSession = Depends(async_get_db),
):
    new_task = Task(**task.model_dump(), created_by_id=user.id)
    db.add(new_task)
    
    await db.flush()

    activity = ActivityLog(
        user_id=user.id,
        action_type="TASK_CREATED",
        resource_id=new_task.id
    )
    db.add(activity)

    await db.commit()
    await db.refresh(new_task)
    
    return new_task
