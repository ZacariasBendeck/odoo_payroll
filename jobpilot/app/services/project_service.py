from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session, joinedload

from app.models.project import Goal, Milestone, Project, Task
from app.schemas.project import (
    GoalCreate,
    GoalUpdate,
    MilestoneCreate,
    MilestoneUpdate,
    ProjectCreate,
    ProjectUpdate,
    TaskCreate,
    TaskUpdate,
)


# --- Projects ---


def list_projects(
    db: Session, status: str | None = None, priority: str | None = None
) -> list[Project]:
    q = db.query(Project)
    if status:
        q = q.filter(Project.status == status)
    if priority:
        q = q.filter(Project.priority == priority)
    return q.order_by(Project.updated_at.desc()).all()


def get_project(db: Session, project_id: int) -> Project | None:
    return (
        db.query(Project)
        .options(joinedload(Project.goals).joinedload(Goal.milestones))
        .filter(Project.id == project_id)
        .first()
    )


def create_project(db: Session, data: ProjectCreate) -> Project:
    project = Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project_id: int, data: ProjectUpdate) -> Project | None:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int) -> bool:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False
    db.delete(project)
    db.commit()
    return True


def get_project_task_count(db: Session, project_id: int) -> int:
    return db.query(sa_func.count(Task.id)).filter(Task.project_id == project_id).scalar() or 0


# --- Goals ---


def create_goal(db: Session, project_id: int, data: GoalCreate) -> Goal:
    goal = Goal(project_id=project_id, **data.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def update_goal(db: Session, goal_id: int, data: GoalUpdate) -> Goal | None:
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(goal, key, value)
    db.commit()
    db.refresh(goal)
    return goal


def delete_goal(db: Session, goal_id: int) -> bool:
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        return False
    db.delete(goal)
    db.commit()
    return True


# --- Milestones ---


def create_milestone(db: Session, goal_id: int, data: MilestoneCreate) -> Milestone:
    milestone = Milestone(goal_id=goal_id, **data.model_dump())
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


def update_milestone(db: Session, milestone_id: int, data: MilestoneUpdate) -> Milestone | None:
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(milestone, key, value)
    db.commit()
    db.refresh(milestone)
    return milestone


def delete_milestone(db: Session, milestone_id: int) -> bool:
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        return False
    db.delete(milestone)
    db.commit()
    return True


# --- Tasks ---


def list_tasks(
    db: Session,
    project_id: int | None = None,
    status: str | None = None,
    member_id: int | None = None,
) -> list[Task]:
    q = db.query(Task)
    if project_id:
        q = q.filter(Task.project_id == project_id)
    if status:
        q = q.filter(Task.status == status)
    if member_id:
        from app.models.team import TaskAssignment

        q = q.join(TaskAssignment).filter(TaskAssignment.member_id == member_id)
    return q.order_by(Task.created_at.desc()).all()


def get_task(db: Session, task_id: int) -> Task | None:
    return (
        db.query(Task)
        .options(joinedload(Task.assignments))
        .filter(Task.id == task_id)
        .first()
    )


def create_task(db: Session, data: TaskCreate) -> Task:
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task_id: int, data: TaskUpdate) -> Task | None:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> bool:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True
