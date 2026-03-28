"""Loads data from data.json into the database on app startup.

The seed file is the source of truth when managed externally (e.g. via git push).
On each startup, it syncs projects, goals, tasks, and team members by name,
creating new records and updating existing ones.
"""

import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.project import Goal, Milestone, Project, Task
from app.models.team import TaskAssignment, TeamMember

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data.json"


def load_seed_data(db: Session) -> None:
    if not DATA_FILE.exists():
        logger.info("No data.json found, skipping seed.")
        return

    with open(DATA_FILE) as f:
        data = json.load(f)

    logger.info("Syncing data.json to database...")

    # --- Team Members ---
    members_map: dict[str, TeamMember] = {}
    for m in data.get("team", []):
        member = db.query(TeamMember).filter(TeamMember.name == m["name"]).first()
        if member:
            for key in ("email", "phone", "role", "skills", "availability"):
                if key in m:
                    setattr(member, key, m[key])
        else:
            member = TeamMember(
                name=m["name"],
                email=m.get("email"),
                phone=m.get("phone"),
                role=m.get("role"),
                skills=m.get("skills"),
                availability=m.get("availability", "available"),
            )
            db.add(member)
            db.flush()
        members_map[m["name"]] = member

    # --- Projects ---
    for p in data.get("projects", []):
        project = db.query(Project).filter(Project.name == p["name"]).first()
        if project:
            for key in ("description", "status", "priority", "deadline", "notes"):
                if key in p:
                    setattr(project, key, p[key])
        else:
            project = Project(
                name=p["name"],
                description=p.get("description"),
                status=p.get("status", "planning"),
                priority=p.get("priority", "medium"),
                deadline=p.get("deadline"),
                notes=p.get("notes"),
            )
            db.add(project)
            db.flush()

        # --- Goals ---
        for g in p.get("goals", []):
            goal = (
                db.query(Goal)
                .filter(Goal.project_id == project.id, Goal.title == g["title"])
                .first()
            )
            if goal:
                for key in ("description", "status", "target_date"):
                    if key in g:
                        setattr(goal, key, g[key])
            else:
                goal = Goal(
                    project_id=project.id,
                    title=g["title"],
                    description=g.get("description"),
                    status=g.get("status", "not_started"),
                    target_date=g.get("target_date"),
                )
                db.add(goal)
                db.flush()

            # --- Milestones ---
            for ms in g.get("milestones", []):
                milestone = (
                    db.query(Milestone)
                    .filter(Milestone.goal_id == goal.id, Milestone.title == ms["title"])
                    .first()
                )
                if milestone:
                    for key in ("description", "status", "due_date"):
                        if key in ms:
                            setattr(milestone, key, ms[key])
                else:
                    milestone = Milestone(
                        goal_id=goal.id,
                        title=ms["title"],
                        description=ms.get("description"),
                        status=ms.get("status", "not_started"),
                        due_date=ms.get("due_date"),
                    )
                    db.add(milestone)
                    db.flush()

        # --- Tasks ---
        for t in p.get("tasks", []):
            task = (
                db.query(Task)
                .filter(Task.project_id == project.id, Task.title == t["title"])
                .first()
            )
            if task:
                for key in ("description", "status", "priority", "due_date", "estimated_hours"):
                    if key in t:
                        setattr(task, key, t[key])
            else:
                task = Task(
                    project_id=project.id,
                    title=t["title"],
                    description=t.get("description"),
                    status=t.get("status", "todo"),
                    priority=t.get("priority", "medium"),
                    due_date=t.get("due_date"),
                    estimated_hours=t.get("estimated_hours"),
                )
                db.add(task)
                db.flush()

            # --- Task Assignments ---
            for assignee_name in t.get("assigned_to", []):
                member = members_map.get(assignee_name)
                if not member:
                    continue
                existing = (
                    db.query(TaskAssignment)
                    .filter(
                        TaskAssignment.task_id == task.id,
                        TaskAssignment.member_id == member.id,
                    )
                    .first()
                )
                if not existing:
                    db.add(TaskAssignment(task_id=task.id, member_id=member.id))

    db.commit()
    logger.info("Data sync complete.")
