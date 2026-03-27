from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.team import (
    TeamMemberCreate,
    TeamMemberResponse,
    TeamMemberUpdate,
)
from app.services import team_service

router = APIRouter(prefix="/api/team", tags=["team"])


@router.get("", response_model=list[TeamMemberResponse])
def list_members(db: Session = Depends(get_db)):
    members = team_service.list_members(db)
    result = []
    for m in members:
        resp = TeamMemberResponse.model_validate(m)
        resp.active_tasks = team_service.get_member_active_task_count(db, m.id)
        result.append(resp)
    return result


@router.post("", response_model=TeamMemberResponse, status_code=201)
def create_member(data: TeamMemberCreate, db: Session = Depends(get_db)):
    member = team_service.create_member(db, data)
    return TeamMemberResponse.model_validate(member)


@router.get("/{member_id}", response_model=TeamMemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = team_service.get_member(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    resp = TeamMemberResponse.model_validate(member)
    resp.active_tasks = team_service.get_member_active_task_count(db, member_id)
    return resp


@router.put("/{member_id}", response_model=TeamMemberResponse)
def update_member(
    member_id: int, data: TeamMemberUpdate, db: Session = Depends(get_db)
):
    member = team_service.update_member(db, member_id, data)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return TeamMemberResponse.model_validate(member)


@router.delete("/{member_id}", status_code=204)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    if not team_service.delete_member(db, member_id):
        raise HTTPException(status_code=404, detail="Member not found")


@router.get("/{member_id}/workload")
def get_workload(member_id: int, db: Session = Depends(get_db)):
    member = team_service.get_member(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    assignments = team_service.get_member_workload(db, member_id)
    return {
        "member": member.name,
        "active_assignments": len(assignments),
        "tasks": [
            {
                "task_id": a.task_id,
                "task_title": a.task.title if a.task else "",
                "status": a.status,
                "assigned_at": a.assigned_at,
            }
            for a in assignments
        ],
    }
