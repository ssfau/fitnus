# db.py
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, ForeignKey, JSON, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Mapped, mapped_column
from typing import List, Dict
from datetime import date

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Workout Models
class WorkoutTemplate(Base):
    __tablename__ = "workout_templates"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    is_weekly: Mapped[bool] = mapped_column(Boolean, default=True)  # True for weekly, False for single day
    template_data: Mapped[dict] = mapped_column(JSON)  # Stores day -> exercises mapping
    created_at: Mapped[date] = mapped_column(Date, default=date.today)
    
    # Relationship to workout plans
    plans: Mapped[List["WorkoutPlan"]] = relationship("WorkoutPlan", back_populates="template", cascade="all, delete-orphan")


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("workout_templates.id"), nullable=True)
    week_start: Mapped[date] = mapped_column(Date, index=True)  # ISO date for week start (Monday)
    plan_data: Mapped[dict] = mapped_column(JSON)  # Stores day -> exercises for this specific week
    created_at: Mapped[date] = mapped_column(Date, default=date.today)
    
    # Relationship to template
    template: Mapped["WorkoutTemplate"] = relationship("WorkoutTemplate", back_populates="plans")


class WorkoutHistory(Base):
    __tablename__ = "workout_history"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    completed_exercises: Mapped[list] = mapped_column(JSON)  # List of exercises with weight/reps
    created_at: Mapped[date] = mapped_column(Date, default=date.today)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


