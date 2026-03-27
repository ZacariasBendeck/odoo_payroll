from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import project_service, team_service

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    projects = project_service.list_projects(db)
    tasks = project_service.list_tasks(db)
    members = team_service.list_members(db)

    stats = {
        "total_projects": len(projects),
        "active_projects": len([p for p in projects if p.status == "active"]),
        "total_tasks": len(tasks),
        "pending_tasks": len([t for t in tasks if t.status == "todo"]),
        "in_progress_tasks": len([t for t in tasks if t.status == "in_progress"]),
        "completed_tasks": len([t for t in tasks if t.status == "done"]),
        "team_size": len(members),
    }

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "projects": projects, "stats": stats, "tasks": tasks[:10]},
    )


@router.get("/projects")
def projects_page(
    request: Request,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    projects = project_service.list_projects(db, status=status)
    return templates.TemplateResponse(
        "projects/list.html",
        {"request": request, "projects": projects, "current_status": status},
    )


@router.get("/projects/{project_id}")
def project_detail(request: Request, project_id: int, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if not project:
        return templates.TemplateResponse(
            "dashboard.html", {"request": request, "error": "Project not found"}
        )
    tasks = project_service.list_tasks(db, project_id=project_id)
    members = team_service.list_members(db)
    return templates.TemplateResponse(
        "projects/detail.html",
        {"request": request, "project": project, "tasks": tasks, "members": members},
    )


@router.get("/team")
def team_page(request: Request, db: Session = Depends(get_db)):
    members = team_service.list_members(db)
    members_data = []
    for m in members:
        members_data.append(
            {
                "member": m,
                "active_tasks": team_service.get_member_active_task_count(db, m.id),
            }
        )
    return templates.TemplateResponse(
        "team/list.html", {"request": request, "members_data": members_data}
    )


@router.get("/inbox")
def inbox_page(request: Request, db: Session = Depends(get_db)):
    from app.models.integration import ActionItem

    items = (
        db.query(ActionItem).order_by(ActionItem.created_at.desc()).limit(50).all()
    )
    return templates.TemplateResponse(
        "inbox.html", {"request": request, "action_items": items}
    )
