from fastapi import APIRouter, Depends, HTTPException, Header, Query
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta

from backend.db import get_db
import backend.schemas as schemas
from backend.core.workout_logic import (
    get_motivational_quote,
    create_workout_template,
    get_workout_templates,
    get_workout_template_by_id,
    update_workout_template,
    delete_workout_template,
    assign_template_to_week,
    get_workout_week,
    get_today_workouts,
    complete_workout,
    get_week_start,
    search_exercises
)

router = APIRouter()


def get_user_id(x_user_id: Optional[str] = Header(None, alias="X-User-ID")):
    """Dependency to extract X-User-ID header."""
    if not x_user_id:
        raise HTTPException(status_code=400, detail="X-User-ID header is required")
    return x_user_id


@router.get("/templates")
def fetch_templates(
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    GET /api/workouts/templates
    Fetch saved templates for X-User-ID
    """
    templates = get_workout_templates(db, user_id)
    return [
        {
            "id": t.id,
            "user_id": t.user_id,
            "name": t.name,
            "is_weekly": t.is_weekly,
            "template_data": t.template_data,
            "created_at": t.created_at.isoformat() if t.created_at else None
        }
        for t in templates
    ]


@router.post("/templates")
def create_template(
    template_data: schemas.WorkoutTemplateCreate,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    POST /api/workouts/templates
    Create a workout template (one-week or single-day template)
    """
    template = create_workout_template(db, user_id, template_data)
    return {
        "id": template.id,
        "user_id": template.user_id,
        "name": template.name,
        "is_weekly": template.is_weekly,
        "template_data": template.template_data,
        "created_at": template.created_at.isoformat() if template.created_at else None
    }


@router.get("/week/{week_start}")
def fetch_week_plan(
    week_start: str,
    auto_generated: Optional[bool] = Query(default=False, description="Return auto-generated if no saved plan exists"),
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    GET /api/workouts/week/{week_start}
    Fetch a generated or saved week plan (week_start ISO date, optional query to specify auto-generated vs saved)
    """
    try:
        week_start_date = datetime.strptime(week_start, "%Y-%m-%d").date()
        # Ensure it's a Monday
        week_start_date = get_week_start(week_start_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="week_start must be in YYYY-MM-DD format")
    
    result = get_workout_week(db, user_id, week_start_date, auto_generated)
    
    if result is None:
        raise HTTPException(status_code=404, detail="No workout plan found for this week")
    
    return result


@router.post("/complete")
def submit_completed_workout(
    workout_data: schemas.WorkoutCompleteRequest,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    POST /api/workouts/complete
    Submit a finished workout for a given date (ONLY finished workout payload; backend records history and updates streaks)
    """
    try:
        result = complete_workout(db, user_id, workout_data.date, workout_data.completed_exercises)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/templates/{template_id}")
def update_template(
    template_id: int,
    update_data: schemas.WorkoutTemplateUpdate,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    PUT /api/workouts/templates/{template_id}
    Update template
    """
    template = update_workout_template(db, template_id, user_id, update_data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "id": template.id,
        "user_id": template.user_id,
        "name": template.name,
        "is_weekly": template.is_weekly,
        "template_data": template.template_data,
        "created_at": template.created_at.isoformat() if template.created_at else None
    }


@router.delete("/templates/{template_id}")
def delete_template(
    template_id: int,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    DELETE /api/workouts/templates/{template_id}
    Delete template
    """
    success = delete_workout_template(db, template_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"message": "Template deleted successfully"}


@router.post("/templates/{template_id}/assign")
def assign_template(
    template_id: int,
    week_start: str,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    POST /api/workouts/templates/{template_id}/assign
    Assign a template to a specific week (week_start should be ISO date, will be normalized to Monday)
    """
    try:
        week_start_date = datetime.strptime(week_start, "%Y-%m-%d").date()
        week_start_date = get_week_start(week_start_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="week_start must be in YYYY-MM-DD format")
    
    try:
        plan = assign_template_to_week(db, user_id, template_id, week_start_date)
        return {
            "id": plan.id,
            "user_id": plan.user_id,
            "template_id": plan.template_id,
            "week_start": plan.week_start.isoformat(),
            "plan_data": plan.plan_data
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Additional helper endpoint for workout home page
@router.get("/home")
def get_workout_home(
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    GET /api/workouts/home
    Get workout home page data: motivational quote and today's workouts
    """
    today = date.today()
    quote = get_motivational_quote()
    today_workouts = get_today_workouts(db, user_id, today)
    
    return {
        "motivational_quote": quote,
        "today_workouts": today_workouts
    }


@router.get("/exercises/search")
def search_exercises_endpoint(
    q: str = Query(..., description="Exercise search query"),
    user_id: str = Depends(get_user_id)
):
    """
    GET /api/workouts/exercises/search?q={query}
    Search for exercises using ExerciseDB API. Returns exercise data to frontend.
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    exercises = search_exercises(q.strip())
    return exercises