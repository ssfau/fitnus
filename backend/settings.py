from fastapi import APIRouter
from sqlalchemy import Column, Integer, Float, String, Boolean
from sqlalchemy.orm import Session, Mapped, mapped_column
from db import Base
import schemas

router = APIRouter()

class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    height: Mapped[float] = mapped_column(Float)     # cm
    weight: Mapped[float] = mapped_column(Float)     # kg
    age: Mapped[int] = mapped_column(Integer)
    sex: Mapped[str] = mapped_column(String)         # "male" / "female"
    goal: Mapped[str] = mapped_column(String)        # "lose" / "gain" / "maintain"
    activity: Mapped[str] = mapped_column(String)
    experience: Mapped[str] = mapped_column(String)

def get_settings(db: Session, data: schemas.UserConfigCreate):
    user = db.query(UserSettings).filter_by(user_id=data.user_id).first()
    if user:
        return user
    return _create_user(db, data)


def save_settings(db: Session, data: schemas.UserConfigCreate):
    user = db.query(UserSettings).filter_by(user_id=data.user_id).first()

    if user:
        # update
        for key, value in data.dict().items():
            setattr(user, key, value)
        db.commit()
        return user

    return _create_user(db, data)


# helper function for creating a new user
def _create_user(db: Session, data: schemas.UserConfigCreate):
    new_user = UserSettings(**data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user




