from auth import require_roles
from fastapi import APIRouter, Depends, HTTPException
from core.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import schemas
from schemas.team import UserTeamResponse, UserTeamCreate
from models.user import User
from models.task import Task
from models.team import UserTeam, Team
from auth import hash_password, verify_password, create_access_token

taskUpdateRouter = APIRouter()


@taskUpdateRouter.patch("/assign-task",response_model=schemas.task.TaskResponse)
async def assign_tasks(task_data:schemas.task.UpdateTaskTeam,user:User=Depends(require_roles("manager")),db:AsyncSession=Depends(async_get_db)):
    query=select(Task).where(Task.id==task_data.task_id)
    existing_record=await db.execute(query)
    existing_record=existing_record.scalars().first()

    if existing_record.team_id is not None or existing_record.assignee_id is not None:
        raise HTTPException(status_code=400,detail="task pehle se assign h")

    db_user = await db.execute(select(User).where(User.id == task_data.assignee_id))
    db_user = db_user.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="user nhi h")

    db_team = await db.execute(select(Team).where(Team.id == task_data.team_id))
    db_team = db_team.scalars().first()
    if not db_team:
        raise HTTPException(status_code=404, detail="team nhi h")

    if db_team.created_by_id!=user.id:
        raise HTTPException(status_code=403,detail="apna team dekho bhai, dusre me nhi aana")

    existing_record.team_id=task_data.team_id
    existing_record.assignee_id=task_data.assignee_id
    await db.commit()
    await db.refresh(existing_record)
    db.close()
    return existing_record