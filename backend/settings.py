from sqlalchemy import Column, Integer, Float, String, Boolean
from sqlalchemy.orm import Session
from db import Base
import schemas

class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(Integer, primary_key=True) 
    height = Column(Float)     # cm
    weight = Column(Float)     # kg
    age = Column(Integer)
    sex = Column(String)       # "male" / "female"
    goal = Column(String)      # "lose" / "gain" / "maintain"
    activity = Column(String)
    experience = Column(String)

def save_settings(db: Session, data: schemas.UserSettingsCreate):
    existing = db.query(schemas.UserSettingsBase).filter_by(user_id=data.user_id).first()

    if existing:
        # update
        for key, value in data.dict().items():
            setattr(existing, key, value)
        db.commit()
        return existing

    # create
    new_user = schemas.UserSettingsBase(**data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



