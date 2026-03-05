from auth import require_roles
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from core.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas.task import TaskResponse, UpdateTaskTeam, UpdateTask
from models.user import User
from models.task import Task
from models.team import Team
from utils.helper import send_task_completion_email

taskUpdateRouter = APIRouter()


@taskUpdateRouter.patch("/assign-task", response_model=TaskResponse)
async def assign_tasks(
    task_data: UpdateTaskTeam,
    user: User = Depends(require_roles("manager")),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(Task).where(Task.id == task_data.task_id)
    existing_record = await db.execute(query)
    existing_record = existing_record.scalars().first()

    if not existing_record:
        raise HTTPException(status_code=404, detail="Task not found")

    if existing_record.team_id is not None or existing_record.assignee_id is not None:
        raise HTTPException(
            status_code=400, detail="Task is already assigned to a team or user"
        )

    db_user = await db.execute(select(User).where(User.id == task_data.assignee_id))
    db_user = db_user.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Assignee user not found")

    db_team = await db.execute(select(Team).where(Team.id == task_data.team_id))
    db_team = db_team.scalars().first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Specified team not found")

    if db_team.created_by_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You can only assign tasks to teams created by you",
        )

    existing_record.team_id = task_data.team_id
    existing_record.assignee_id = task_data.assignee_id
    await db.commit()
    await db.refresh(existing_record)
    db.close()
    return existing_record


@taskUpdateRouter.patch("/update-task", response_model=TaskResponse)
async def update_task(
    background_tasks: BackgroundTasks,
    task_data: UpdateTask,
    user: User = Depends(require_roles("admin", "manager", "user")),
    db: AsyncSession = Depends(async_get_db),
):
    query = select(Task).where(Task.id == task_data.task_id)
    existing_record = await db.execute(query)
    existing_record = existing_record.scalars().first()

    if not existing_record:
        raise HTTPException(status_code=404, detail="Task not found")

    if existing_record.created_by_id != user.id and user.role == "manager":
        raise HTTPException(
            status_code=403,
            detail="Permission denied: You do not have authority to modify this task",
        )
    if (
        task_data.status
        and task_data.status.lower() == "done"
        and existing_record.status != "done"
        and user.role == "user"
    ):
        background_tasks.add_task(
            send_task_completion_email, user.email, existing_record.title
        )

    if user.role == "admin" or user.role == "manager":
        if task_data.title:
            existing_record.title = task_data.title
        if task_data.description:
            existing_record.description = task_data.description
        if task_data.priority:
            existing_record.priority = task_data.priority
        if task_data.assign_id:
            existing_record.assignee_id = task_data.assign_id

    if task_data.status:
        existing_record.status = task_data.status

    await db.commit()
    await db.refresh(existing_record)
    db.close()
    return existing_record
