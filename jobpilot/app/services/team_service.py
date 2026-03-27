from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from app.models.team import TaskAssignment, TeamMember
from app.schemas.team import TeamMemberCreate, TeamMemberUpdate


def list_members(db: Session) -> list[TeamMember]:
    return db.query(TeamMember).order_by(TeamMember.name).all()


def get_member(db: Session, member_id: int) -> TeamMember | None:
    return db.query(TeamMember).filter(TeamMember.id == member_id).first()


def create_member(db: Session, data: TeamMemberCreate) -> TeamMember:
    member = TeamMember(**data.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def update_member(db: Session, member_id: int, data: TeamMemberUpdate) -> TeamMember | None:
    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not member:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(member, key, value)
    db.commit()
    db.refresh(member)
    return member


def delete_member(db: Session, member_id: int) -> bool:
    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not member:
        return False
    db.delete(member)
    db.commit()
    return True


def get_member_active_task_count(db: Session, member_id: int) -> int:
    return (
        db.query(sa_func.count(TaskAssignment.id))
        .filter(
            TaskAssignment.member_id == member_id,
            TaskAssignment.status.in_(["assigned", "accepted", "in_progress"]),
        )
        .scalar()
        or 0
    )


def assign_task(
    db: Session, task_id: int, member_id: int, notes: str | None = None
) -> TaskAssignment:
    assignment = TaskAssignment(
        task_id=task_id, member_id=member_id, notes=notes
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def get_member_workload(db: Session, member_id: int) -> list[TaskAssignment]:
    return (
        db.query(TaskAssignment)
        .filter(
            TaskAssignment.member_id == member_id,
            TaskAssignment.status.in_(["assigned", "accepted", "in_progress"]),
        )
        .all()
    )
