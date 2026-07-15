from sqlalchemy.orm import Session

from models.membership_plan import MembershipPlan


def list_for_gym(db: Session, gym_id: int) -> list[MembershipPlan]:
    return db.query(MembershipPlan).filter(MembershipPlan.gym_id == gym_id).all()


def list_active_for_gym(db: Session, gym_id: int) -> list[MembershipPlan]:
    return (
        db.query(MembershipPlan)
        .filter(MembershipPlan.gym_id == gym_id, MembershipPlan.is_active.is_(True))
        .all()
    )


def get_in_gym(db: Session, plan_id: int, gym_id: int) -> MembershipPlan | None:
    return (
        db.query(MembershipPlan)
        .filter(MembershipPlan.id == plan_id, MembershipPlan.gym_id == gym_id)
        .first()
    )


def create(db: Session, plan: MembershipPlan) -> MembershipPlan:
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def save(db: Session, plan: MembershipPlan) -> MembershipPlan:
    db.commit()
    db.refresh(plan)
    return plan


def delete(db: Session, plan: MembershipPlan) -> None:
    db.delete(plan)
    db.commit()
