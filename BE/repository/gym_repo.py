from sqlalchemy.orm import Session

from models.gym import Gym


def get_by_id(db: Session, gym_id: int) -> Gym | None:
    return db.query(Gym).filter(Gym.id == gym_id).first()


def create(db: Session, gym: Gym) -> Gym:
    db.add(gym)
    db.commit()
    db.refresh(gym)
    return gym
