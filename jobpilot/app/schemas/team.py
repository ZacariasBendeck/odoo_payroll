from datetime import datetime

from pydantic import BaseModel


class TeamMemberCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    role: str | None = None
    skills: str | None = None
    availability: str = "available"


class TeamMemberUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    role: str | None = None
    skills: str | None = None
    availability: str | None = None


class TeamMemberResponse(BaseModel):
    id: int
    name: str
    email: str | None
    phone: str | None
    role: str | None
    skills: str | None
    availability: str
    created_at: datetime
    active_tasks: int = 0

    model_config = {"from_attributes": True}


class TaskAssignmentCreate(BaseModel):
    member_id: int
    notes: str | None = None


class TaskAssignmentResponse(BaseModel):
    id: int
    task_id: int
    member_id: int
    member_name: str = ""
    assigned_at: datetime
    status: str
    notes: str | None

    model_config = {"from_attributes": True}
