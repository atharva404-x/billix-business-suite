import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.roles import UserRole


class UserMinimalResponse(BaseModel):
    id: uuid.UUID
    clerk_id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class MemberAdd(BaseModel):
    email: EmailStr = Field(..., description="The registered email of the user to be added")
    role: UserRole = Field(UserRole.VIEWER, description="Role to assign within the business")


class MembershipResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    business_id: uuid.UUID
    role: UserRole
    is_active: bool
    invited_by: Optional[uuid.UUID] = None
    joined_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Nested user information to list member details
    user: Optional[UserMinimalResponse] = None

    model_config = ConfigDict(from_attributes=True)
