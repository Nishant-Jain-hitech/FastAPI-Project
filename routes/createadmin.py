from models import User
from core.database import async_get_db, get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import APIRouter

import schemas.user


router=APIRouter(prefix="/api")


@router.post('/create-admin',response_model=schemas.user.UserResponse|dict)
async def create_admin(db:AsyncSession=Depends(async_get_db)):
    user={
        "name":"admin1",
        "email":"admin1@gmail.com",
        "password":"abcAb123@",
        "role":"admin"
    }

    db_user=User(**user)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    db.close()
    
    return {"message":"ban gya admin!"}