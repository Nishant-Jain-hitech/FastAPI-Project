from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from auth import require_roles
from core.database import async_get_db
from schemas.task import TaskResponse, TaskCreate, UpdateTask, TaskBulkDelete
from models.task import Task
from models.user import User

taskBulkRouter = APIRouter()


@taskBulkRouter.post("/bulk-create", response_model=List[TaskResponse])
async def bulk_create_tasks(
    tasks: List[TaskCreate],
    user: User = Depends(require_roles("admin", "manager")),
    db: AsyncSession = Depends(async_get_db),
):
    if not tasks:
        raise HTTPException(status_code=400, detail="Task list cannot be empty")

    new_tasks = [Task(**task.model_dump(), created_by_id=user.id) for task in tasks]

    try:
        db.add_all(new_tasks)
        await db.commit()

        for task in new_tasks:
            await db.refresh(task)

        return new_tasks
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Bulk upload failed")


@taskBulkRouter.patch("/bulk-update", response_model=List[TaskResponse])
async def bulk_update_tasks(
    updates: List[UpdateTask],
    user: User = Depends(require_roles("admin", "manager")),
    db: AsyncSession = Depends(async_get_db),
):
    if not updates:
        raise HTTPException(status_code=400, detail="Update list cannot be empty")

    task_ids = [u.task_id for u in updates]
    query = select(Task).where(Task.id.in_(task_ids))
    result = await db.execute(query)
    existing_tasks = {t.id: t for t in result.scalars().all()}

    if len(existing_tasks) != len(task_ids):
        raise HTTPException(status_code=404, detail="Kuch task IDs database mein nahi mile")

    updated_objects = []
    for update_data in updates:
        target_task = existing_tasks.get(update_data.task_id)

        if user.role == "manager" and target_task.created_by_id != user.id:
            raise HTTPException(
                status_code=403, 
                detail=f"Task {target_task.id} aapki nahi hai, update nahi kar sakte"
            )

        update_dict = update_data.model_dump(exclude_unset=True, exclude={"task_id"})
        for key, value in update_dict.items():
            setattr(target_task, key, value)

        updated_objects.append(target_task)

    try:
        await db.commit()
        for t in updated_objects:
            await db.refresh(t)
        return updated_objects
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Bulk update failed")


@taskBulkRouter.delete("/bulk-delete")
async def bulk_delete_tasks(
    data: TaskBulkDelete,
    user: User = Depends(require_roles("admin", "manager")),
    db: AsyncSession = Depends(async_get_db),
):
    try:
        fetch_query = select(Task).where(Task.id.in_(data.task_ids))
        fetch_result = await db.execute(fetch_query)
        existing_tasks = fetch_result.scalars().all()
        existing_ids = {t.id for t in existing_tasks}

        if len(existing_ids) != len(data.task_ids):
            raise HTTPException(
                status_code=404, detail="Kuch task IDs database mein nahi mile"
            )

        if user.role == "manager":
            unauthorized_tasks = [
                t for t in existing_tasks if t.created_by_id != user.id
            ]
            if unauthorized_tasks:
                raise HTTPException(
                    status_code=403,
                    detail="Aap kisi aur manager ki task delete nahi kar sakte",
                )

        delete_query = delete(Task).where(Task.id.in_(data.task_ids))
        await db.execute(delete_query)
        await db.commit()

        return {"message": "Bulk delete successful"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error during bulk delete {e}")
