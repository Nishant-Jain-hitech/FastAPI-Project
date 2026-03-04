from models import User
from core.database import async_get_db, get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import APIRouter

import schemas.user
from auth import hash_password


router = APIRouter(prefix="/api")


@router.post("/create-admin", response_model=schemas.user.UserResponse | dict)
async def create_admin(db: AsyncSession = Depends(async_get_db)):
    hashed_password = hash_password("abcAb123@")
    user = {
        "name": "admin",
        "email": "admin@gmail.com",
        "password": hashed_password,
        "role": "admin",
    }

    db_user = User(**user)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    db.close()

    return {"message": "Administrator account successfully created"}
