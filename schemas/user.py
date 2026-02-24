from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, Field
from uuid import UUID
from models.enums import UserRole
from typing import Optional


"""Create Model"""


class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole

    @field_validator("name")
    def name_must_not_be_empty(cls, v: str) -> str:
        cleaned_name = v.strip()
        if not cleaned_name:
            raise ValueError("Name cannot be empty or just whitespace")
        return cleaned_name


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserLogin(BaseModel):
    email:EmailStr
    password:str


"""Response Model"""


class UserResponse(UserBase):
    id: UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserLoginResponse(BaseModel):
    access_token: str


"""Update User"""


class UpdateUser(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str] = Field(..., min_length=8)
    role: Optional[UserRole]
    is_active: Optional[bool]
