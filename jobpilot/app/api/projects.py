from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.project import (
    GoalCreate,
    GoalResponse,
    GoalUpdate,
    MilestoneCreate,
    MilestoneResponse,
    MilestoneUpdate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services import project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    status: str | None = None,
    priority: str | None = None,
    db: Session = Depends(get_db),
):
    projects = project_service.list_projects(db, status=status, priority=priority)
    result = []
    for p in projects:
        resp = ProjectResponse.model_validate(p)
        resp.task_count = project_service.get_project_task_count(db, p.id)
        result.append(resp)
    return result


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    project = project_service.create_project(db, data)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    resp = ProjectResponse.model_validate(project)
    resp.task_count = project_service.get_project_task_count(db, project_id)
    return resp


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = project_service.update_project(db, project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    if not project_service.delete_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")


# --- Goals ---
@router.post("/{project_id}/goals", response_model=GoalResponse, status_code=201)
def create_goal(project_id: int, data: GoalCreate, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    goal = project_service.create_goal(db, project_id, data)
    return GoalResponse.model_validate(goal)


@router.put("/goals/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: int, data: GoalUpdate, db: Session = Depends(get_db)):
    goal = project_service.update_goal(db, goal_id, data)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return GoalResponse.model_validate(goal)


@router.delete("/goals/{goal_id}", status_code=204)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    if not project_service.delete_goal(db, goal_id):
        raise HTTPException(status_code=404, detail="Goal not found")


# --- Milestones ---
@router.post("/goals/{goal_id}/milestones", response_model=MilestoneResponse, status_code=201)
def create_milestone(goal_id: int, data: MilestoneCreate, db: Session = Depends(get_db)):
    milestone = project_service.create_milestone(db, goal_id, data)
    return MilestoneResponse.model_validate(milestone)


@router.put("/milestones/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(
    milestone_id: int, data: MilestoneUpdate, db: Session = Depends(get_db)
):
    milestone = project_service.update_milestone(db, milestone_id, data)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return MilestoneResponse.model_validate(milestone)


@router.delete("/milestones/{milestone_id}", status_code=204)
def delete_milestone(milestone_id: int, db: Session = Depends(get_db)):
    if not project_service.delete_milestone(db, milestone_id):
        raise HTTPException(status_code=404, detail="Milestone not found")
