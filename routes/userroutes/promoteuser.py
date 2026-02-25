# from pydantic._internal._decorators import RootValidatorDecoratorInfo
# from fastapi import HTTPException
# from uuid import UUID
# from auth import require_roles
# from fastapi import APIRouter, Depends
# from core.database import async_get_db
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select

# from schemas.user import UserResponse, RoleChangeRequest
# from models.user import User


# changeRoleRouter=APIRouter()


# @changeRoleRouter.patch('/{user_id}/change-role',response_model=UserResponse)
# async def change_role(
#     user_id:UUID,
#     role_data:RoleChangeRequest,
#     user:User=Depends(require_roles("admin")),
#     db:AsyncSession=Depends(async_get_db)
# ):
#     query=select(User).where(User.id==user_id)
#     result=await db.execute(query)
#     result= result.scalars().first()

#     if not result:
#         raise HTTPException(status_code=404, detail="user nhi h")

#     if result.role=="admin":
#         raise HTTPException(status_code=400, detail="admin ka role change nhi karna")

#     if result.role==role_data.role:
#         raise HTTPException(status_code=400, detail="already same role me h")

#     if result.role=="manager" and role_data.role=="user":
#         raise HTTPException(status_code=400, detail="manager ko user nhi bana sakte")

#     if result.role=="manager" and role_data.role=="admin":
#         raise HTTPException(status_code=400, detail="manager ko admin nhi bana sakte")

#     result.role=role_data.role
#     await db.commit()
#     await db.refresh(result)
#     return result
