from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.project import TaskCreate, TaskResponse, TaskUpdate
from app.schemas.team import TaskAssignmentCreate, TaskAssignmentResponse
from app.services import project_service, team_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    project_id: int | None = None,
    status: str | None = None,
    member_id: int | None = None,
    db: Session = Depends(get_db),
):
    tasks = project_service.list_tasks(
        db, project_id=project_id, status=status, member_id=member_id
    )
    result = []
    for t in tasks:
        resp = TaskResponse.model_validate(t)
        resp.assignee_names = [a.member.name for a in t.assignments if a.member]
        result.append(resp)
    return result


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task = project_service.create_task(db, data)
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = project_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    resp = TaskResponse.model_validate(task)
    resp.assignee_names = [a.member.name for a in task.assignments if a.member]
    return resp


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    task = project_service.update_task(db, task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    if not project_service.delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("/{task_id}/assign", response_model=TaskAssignmentResponse, status_code=201)
def assign_task(
    task_id: int, data: TaskAssignmentCreate, db: Session = Depends(get_db)
):
    task = project_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    member = team_service.get_member(db, data.member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    assignment = team_service.assign_task(db, task_id, data.member_id, data.notes)
    resp = TaskAssignmentResponse.model_validate(assignment)
    resp.member_name = member.name
    return resp
