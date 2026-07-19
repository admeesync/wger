from datetime import date

from sqlalchemy.orm import Session

from models.attendance import Attendance


def list_for_gym(db: Session, gym_id: int, limit: int = 200) -> list[Attendance]:
    return (
        db.query(Attendance)
        .filter(Attendance.gym_id == gym_id)
        .order_by(Attendance.date.desc())
        .limit(limit)
        .all()
    )


def list_for_gym_on_date(db: Session, gym_id: int, day: date) -> list[Attendance]:
    return db.query(Attendance).filter(Attendance.gym_id == gym_id, Attendance.date == day).all()


def list_for_member_since(db: Session, member_id: int, since: date) -> list[Attendance]:
    return (
        db.query(Attendance)
        .filter(Attendance.member_id == member_id, Attendance.date >= since)
        .order_by(Attendance.date.desc())
        .all()
    )


def get_open_for_member(db: Session, member_id: int, day: date) -> Attendance | None:
    return (
        db.query(Attendance)
        .filter(Attendance.member_id == member_id, Attendance.date == day, Attendance.time_out.is_(None))
        .first()
    )


def get_for_member_on_date(db: Session, member_id: int, day: date) -> Attendance | None:
    return db.query(Attendance).filter(Attendance.member_id == member_id, Attendance.date == day).first()


def create(db: Session, attendance: Attendance) -> Attendance:
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


def save(db: Session, attendance: Attendance) -> Attendance:
    db.commit()
    db.refresh(attendance)
    return attendance
