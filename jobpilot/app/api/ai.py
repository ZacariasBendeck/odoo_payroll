import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ai import (
    AIAnalysisResponse,
    AIDashboardSummary,
    AIDelegationResponse,
    AIExtractActionsRequest,
    AIExtractActionsResponse,
    DelegationRecommendation,
    ExtractedAction,
)
from app.services import ai_service, project_service, team_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["ai"])


def _project_to_dict(project, db: Session) -> dict:
    tasks = project_service.list_tasks(db, project_id=project.id)
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "priority": project.priority,
        "deadline": str(project.deadline) if project.deadline else None,
        "goals": [
            {
                "id": g.id,
                "title": g.title,
                "status": g.status,
                "milestones": [
                    {"id": m.id, "title": m.title, "status": m.status}
                    for m in g.milestones
                ],
            }
            for g in project.goals
        ],
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "assignees": [a.member.name for a in t.assignments if a.member],
            }
            for t in tasks
        ],
    }


@router.post("/plan/{project_id}", response_model=AIAnalysisResponse)
def analyze_project(project_id: int, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_data = _project_to_dict(project, db)

    try:
        result = ai_service.analyze_project(project_data)
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {e}")

    # Save AI suggestions to project
    import json
    project_service.update_project(
        db,
        project_id,
        project_service.ProjectUpdate(
            ai_next_steps=json.dumps(result.get("next_steps", []))
        ),
    )

    return AIAnalysisResponse(
        project_id=project_id,
        summary=result.get("summary", ""),
        next_steps=result.get("next_steps", []),
        risks=result.get("risks", []),
        priority_suggestions=result.get("priority_suggestions", []),
    )


@router.post("/delegate/{project_id}", response_model=AIDelegationResponse)
def recommend_delegation(project_id: int, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get unassigned tasks
    all_tasks = project_service.list_tasks(db, project_id=project_id)
    unassigned = [t for t in all_tasks if not t.assignments]

    if not unassigned:
        return AIDelegationResponse(project_id=project_id, recommendations=[])

    tasks_data = [
        {"id": t.id, "title": t.title, "description": t.description, "priority": t.priority}
        for t in unassigned
    ]

    members = team_service.list_members(db)
    team_data = [
        {
            "id": m.id,
            "name": m.name,
            "role": m.role,
            "skills": m.skills,
            "availability": m.availability,
            "active_tasks": team_service.get_member_active_task_count(db, m.id),
        }
        for m in members
    ]

    try:
        recs = ai_service.recommend_delegation(tasks_data, team_data)
    except Exception as e:
        logger.error(f"AI delegation failed: {e}")
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {e}")

    return AIDelegationResponse(
        project_id=project_id,
        recommendations=[DelegationRecommendation(**r) for r in recs],
    )


@router.post("/extract-actions", response_model=AIExtractActionsResponse)
def extract_actions(data: AIExtractActionsRequest, db: Session = Depends(get_db)):
    projects = project_service.list_projects(db)
    projects_data = [{"id": p.id, "name": p.name, "description": p.description} for p in projects]

    try:
        actions = ai_service.extract_action_items(data.text, projects_data)
    except Exception as e:
        logger.error(f"AI extraction failed: {e}")
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {e}")

    return AIExtractActionsResponse(
        actions=[ExtractedAction(**a) for a in actions]
    )


@router.get("/dashboard-summary", response_model=AIDashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    projects = project_service.list_projects(db, status="active")
    if not projects:
        projects = project_service.list_projects(db)

    projects_data = []
    for p in projects[:10]:  # Limit to avoid huge prompts
        projects_data.append(_project_to_dict(p, db))

    try:
        result = ai_service.generate_dashboard_summary(projects_data)
    except Exception as e:
        logger.error(f"AI summary failed: {e}")
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {e}")

    return AIDashboardSummary(**result)
