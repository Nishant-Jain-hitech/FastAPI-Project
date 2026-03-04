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
            raise ValueError(
                "The name field cannot be empty or consist solely of whitespace"
            )
        return cleaned_name


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters in length")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one numeric character")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


"""Response Model"""


class UserResponse(UserBase):
    id: UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserLoginResponse(BaseModel):
    access_token: str


"""Update User"""


class UpdateUser(BaseModel):
    user_id: UUID
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
