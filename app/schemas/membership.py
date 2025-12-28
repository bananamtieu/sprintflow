from pydantic import BaseModel, EmailStr
from app.models.membership import MembershipRole

class MembershipInvite(BaseModel):
    user_email: EmailStr
    role: MembershipRole = MembershipRole.MEMBER

class MembershipUpdate(BaseModel):
    role: MembershipRole

class MembershipOut(BaseModel):
    id: int
    user_id: int
    project_id: int
    role: MembershipRole

    model_config = {
        "from_attributes": True
    }