from auth import require_roles
from fastapi import APIRouter, Depends
from core.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.task import TaskResponse, TaskCreate
from models.task import Task
from models.user import User

taskBulkRouter = APIRouter()

@taskBulkRouter.post()