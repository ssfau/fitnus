from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from sqlalchemy.orm import Session, Mapped, mapped_column
from datetime import datetime, date
from backend.db import Base
from backend import schemas as schemas


class DailyNutritionLog(Base):
    __tablename__ = "nutrition_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(index=True)
    date: Mapped[date] = mapped_column(Date, index=True)

    calories: Mapped[float] = mapped_column(default=0)
    protein: Mapped[float] = mapped_column(default=0)
    carbs: Mapped[float] = mapped_column(default=0)
    fats: Mapped[float] = mapped_column(default=0)

class MealEntry(Base):
    __tablename__ = "meal_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(index=True)
    date: Mapped[date] = mapped_column(Date, index=True)

    name: Mapped[str] = mapped_column(default="")
    calories: Mapped[float] = mapped_column(default=0)
    protein: Mapped[float] = mapped_column(default=0)
    carbs: Mapped[float] = mapped_column(default=0)
    fats: Mapped[float] = mapped_column(default=0)

"""
def request_daily_nutrition(db: Session, data: schemas.DailyNutritionBase):
    nutritiontoday = DailyNutritionLog(**data.dict())
    db.query()
"""

def create_manual_meal_entry(db: Session, data: schemas.MealCreate):
    # Convert date string to date object
    date_obj = datetime.strptime(data.date, "%Y-%m-%d").date()
    
    # meal entry update - map fat to fats and handle name field
    meal_dict = data.dict()
    meal_dict['date'] = date_obj
    meal_dict['fats'] = meal_dict.pop('fat')  # Convert fat to fats
    meal_dict['name'] = meal_dict.get('description', '')  # Map description to name
    
    meal = MealEntry(**meal_dict)
    db.add(meal)
    db.commit()
    db.refresh(meal)

    # updating daily nutrition log
    existing = (
        db.query(DailyNutritionLog)
        .filter_by(user_id=data.user_id, date=date_obj)
        .first()
    )

    if existing:
        existing.calories += data.calories
        existing.protein += data.protein
        existing.carbs += data.carbs
        existing.fats += data.fat

        db.commit()
        db.refresh(existing)
    else:
        todays = DailyNutritionLog(
            user_id=data.user_id,
            date=date_obj,
            calories=data.calories,
            protein=data.protein,
            carbs=data.carbs,
            fats=data.fat,
        )
        db.add(todays)
        db.commit()
        db.refresh(todays)
    
    return meal


def get_nutrition_log_by_date(db: Session, user_id: str, date_str: str):
    """Get all meal entries and daily nutrition log for a specific date."""
    from datetime import date as date_type
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None
    
    # Get daily nutrition log
    daily_log = (
        db.query(DailyNutritionLog)
        .filter_by(user_id=user_id, date=date_obj)
        .first()
    )
    
    # Get all meal entries for that date
    meal_entries = (
        db.query(MealEntry)
        .filter_by(user_id=user_id, date=date_obj)
        .all()
    )
    
    return {
        "daily_log": daily_log,
        "meal_entries": meal_entries
    }


def get_daily_summary(db: Session, user_id: str, date_str: str):
    """Get daily nutrition summary for dashboard."""
    from datetime import date as date_type
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None
    
    daily_log = (
        db.query(DailyNutritionLog)
        .filter_by(user_id=user_id, date=date_obj)
        .first()
    )
    
    if not daily_log:
        return {
            "date": date_str,
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fats": 0,
            "meal_count": 0
        }
    
    meal_count = (
        db.query(MealEntry)
        .filter_by(user_id=user_id, date=date_obj)
        .count()
    )
    
    return {
        "date": date_str,
        "calories": daily_log.calories,
        "protein": daily_log.protein,
        "carbs": daily_log.carbs,
        "fats": daily_log.fats,
        "meal_count": meal_count
    }


def get_weight_projection(user_id: str):
    """Placeholder function for weight projections."""
    # Placeholder implementation
    return {
        "two_weeks": None,
        "one_month": None,
        "three_months": None
    }

