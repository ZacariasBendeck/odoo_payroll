from datetime import date, datetime

from pydantic import BaseModel


# --- Project ---
class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    status: str = "planning"
    priority: str = "medium"
    deadline: date | None = None
    notes: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    deadline: date | None = None
    notes: str | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    status: str
    priority: str
    deadline: date | None
    notes: str | None
    ai_next_steps: str | None
    created_at: datetime
    updated_at: datetime
    goals: list["GoalResponse"] = []
    task_count: int = 0

    model_config = {"from_attributes": True}


# --- Goal ---
class GoalCreate(BaseModel):
    title: str
    description: str | None = None
    status: str = "not_started"
    target_date: date | None = None


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    target_date: date | None = None


class GoalResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    status: str
    target_date: date | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Milestone ---
class MilestoneCreate(BaseModel):
    title: str
    description: str | None = None
    status: str = "not_started"
    due_date: date | None = None


class MilestoneUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    due_date: date | None = None


class MilestoneResponse(BaseModel):
    id: int
    goal_id: int
    title: str
    description: str | None
    status: str
    due_date: date | None

    model_config = {"from_attributes": True}


# --- Task ---
class TaskCreate(BaseModel):
    project_id: int
    milestone_id: int | None = None
    title: str
    description: str | None = None
    status: str = "todo"
    priority: str = "medium"
    due_date: date | None = None
    estimated_hours: float | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    due_date: date | None = None
    estimated_hours: float | None = None
    milestone_id: int | None = None


class TaskResponse(BaseModel):
    id: int
    project_id: int
    milestone_id: int | None
    title: str
    description: str | None
    status: str
    priority: str
    due_date: date | None
    estimated_hours: float | None
    created_at: datetime
    assignee_names: list[str] = []

    model_config = {"from_attributes": True}
