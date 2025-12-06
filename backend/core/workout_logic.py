from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from sqlalchemy.orm import Session, Mapped, mapped_column
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
import random
import json
import http.client
import urllib.parse
from backend.db import Base, WorkoutTemplate, WorkoutPlan, WorkoutHistory
from backend import schemas as schemas


# Motivational workout quotes
MOTIVATIONAL_QUOTES = [
    "The only bad workout is the one that didn't happen!",
    "Strength doesn't come from what you can do. It comes from overcoming the things you once thought you couldn't.",
    "Your body can stand almost anything. It's your mind you need to convince.",
    "The pain you feel today will be the strength you feel tomorrow.",
    "Don't stop when you're tired. Stop when you're done.",
    "Success isn't always about greatness. It's about consistency.",
    "The hardest lift of all is lifting your butt off the couch!",
    "You don't have to be great to start, but you have to start to be great.",
    "Push yourself because no one else is going to do it for you.",
    "The only workout you'll regret is the one you didn't do.",
    "Your limitation—it's only your imagination.",
    "Take care of your body. It's the only place you have to live.",
    "The difference between try and triumph is just a little umph!",
    "Sweat is just fat crying.",
    "The body achieves what the mind believes."
]


def get_motivational_quote() -> str:
    """Generate a random motivational workout quote."""
    return random.choice(MOTIVATIONAL_QUOTES)


def get_week_start(date_obj: date) -> date:
    """Get the Monday of the week for a given date."""
    days_since_monday = date_obj.weekday()
    return date_obj - timedelta(days=days_since_monday)


def create_workout_template(db: Session, user_id: str, template_data: schemas.WorkoutTemplateCreate) -> WorkoutTemplate:
    """Create a new workout template."""
    template = WorkoutTemplate(
        user_id=user_id,
        name=template_data.name,
        is_weekly=template_data.is_weekly,
        template_data=template_data.template_data,
        created_at=date.today()
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def get_workout_templates(db: Session, user_id: str) -> List[WorkoutTemplate]:
    """Fetch all saved templates for a user."""
    return db.query(WorkoutTemplate).filter(WorkoutTemplate.user_id == user_id).all()


def get_workout_template_by_id(db: Session, template_id: int, user_id: str) -> Optional[WorkoutTemplate]:
    """Get a specific template by ID, ensuring it belongs to the user."""
    return db.query(WorkoutTemplate).filter(
        WorkoutTemplate.id == template_id,
        WorkoutTemplate.user_id == user_id
    ).first()


def update_workout_template(db: Session, template_id: int, user_id: str, update_data: schemas.WorkoutTemplateUpdate) -> Optional[WorkoutTemplate]:
    """Update an existing workout template."""
    template = get_workout_template_by_id(db, template_id, user_id)
    if not template:
        return None
    
    if update_data.name is not None:
        template.name = update_data.name
    if update_data.template_data is not None:
        template.template_data = update_data.template_data
    
    db.commit()
    db.refresh(template)
    return template


def delete_workout_template(db: Session, template_id: int, user_id: str) -> bool:
    """Delete a workout template."""
    template = get_workout_template_by_id(db, template_id, user_id)
    if not template:
        return False
    
    db.delete(template)
    db.commit()
    return True


def assign_template_to_week(db: Session, user_id: str, template_id: int, week_start: date) -> WorkoutPlan:
    """Assign a template to a specific week."""
    template = get_workout_template_by_id(db, template_id, user_id)
    if not template:
        raise ValueError("Template not found")
    
    # Check if a plan already exists for this week
    existing_plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == user_id,
        WorkoutPlan.week_start == week_start
    ).first()
    
    if existing_plan:
        # Update existing plan
        existing_plan.template_id = template_id
        existing_plan.plan_data = template.template_data
        db.commit()
        db.refresh(existing_plan)
        return existing_plan
    
    # Create new plan
    plan = WorkoutPlan(
        user_id=user_id,
        template_id=template_id,
        week_start=week_start,
        plan_data=template.template_data,
        created_at=date.today()
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_workout_week(db: Session, user_id: str, week_start: date, auto_generated: bool = False) -> Optional[Dict]:
    """Fetch a generated or saved week plan."""
    # Try to get saved plan first
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == user_id,
        WorkoutPlan.week_start == week_start
    ).first()
    
    if plan:
        return {
            "week_start": week_start.isoformat(),
            "plan_data": plan.plan_data,
            "is_auto_generated": False
        }
    
    # If auto_generated is requested and no plan exists, return empty structure
    if auto_generated:
        return {
            "week_start": week_start.isoformat(),
            "plan_data": {},
            "is_auto_generated": True
        }
    
    return None


def get_today_workouts(db: Session, user_id: str, today: date) -> List[Dict]:
    """Get workouts planned for today."""
    week_start = get_week_start(today)
    day_name = today.strftime("%A")  # Monday, Tuesday, etc.
    
    # Get the plan for this week
    plan = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == user_id,
        WorkoutPlan.week_start == week_start
    ).first()
    
    if not plan or not plan.plan_data:
        return []
    
    # Get workouts for today's day name
    today_workouts = plan.plan_data.get(day_name, [])
    return today_workouts if isinstance(today_workouts, list) else []


def complete_workout(db: Session, user_id: str, date_str: str, completed_exercises: List[schemas.CompletedExercise]) -> Dict:
    """Save a completed workout to history and update streaks."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD")
    
    # Convert exercises to JSON-serializable format
    exercises_data = [ex.dict() for ex in completed_exercises]
    
    # Create workout history entry
    history = WorkoutHistory(
        user_id=user_id,
        date=date_obj,
        completed_exercises=exercises_data,
        created_at=date.today()
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    
    # Calculate streak
    streak = calculate_workout_streak(db, user_id, date_obj)
    
    return {
        "id": history.id,
        "user_id": user_id,
        "date": date_str,
        "completed_exercises": exercises_data,
        "streak": streak
    }


def calculate_workout_streak(db: Session, user_id: str, current_date: date) -> int:
    """Calculate the current workout streak for a user."""
    streak = 0
    check_date = current_date
    
    # Check backwards from today
    while True:
        # Check if there's a workout history for this date
        history = db.query(WorkoutHistory).filter(
            WorkoutHistory.user_id == user_id,
            WorkoutHistory.date == check_date
        ).first()
        
        if history:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            # If checking today and no workout, streak is 0
            if check_date == current_date:
                return 0
            # Otherwise, we've found the end of the streak
            break
    
    return streak


def search_exercises(query: str) -> List[Dict]:
    """
    Search for exercises using ExerciseDB API.
    Returns exercise data from the API and terminates.
    """
    headers = {
        'x-rapidapi-key': "5d17cbeadcmshf72174d04376240p163657jsn3af142b41b12",
        'x-rapidapi-host': "exercisedb-api1.p.rapidapi.com"
    }
    
    # URL encode the query
    encoded_query = urllib.parse.quote(query)
    
    # Try first endpoint: /exercises?name=
    conn = http.client.HTTPSConnection("exercisedb-api1.p.rapidapi.com")
    try:
        endpoint = f"/exercises?name={encoded_query}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        if res.status == 200:
            exercises = json.loads(data.decode("utf-8"))
            return exercises if isinstance(exercises, list) else []
    except Exception:
        pass
    finally:
        conn.close()
    
    # If first endpoint doesn't work, try alternative endpoint: /exercises/search?q=
    conn = http.client.HTTPSConnection("exercisedb-api1.p.rapidapi.com")
    try:
        endpoint = f"/exercises/search?q={encoded_query}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        if res.status == 200:
            exercises = json.loads(data.decode("utf-8"))
            return exercises if isinstance(exercises, list) else []
    except Exception:
        pass
    finally:
        conn.close()
    
    # Return empty list if both endpoints fail
    return []
