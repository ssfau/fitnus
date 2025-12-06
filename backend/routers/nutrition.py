from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Form
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from backend.db import get_db
import backend.schemas as schemas
from backend.core.nutrition_logic import (
    create_manual_meal_entry,
    get_nutrition_log_by_date,
    get_daily_summary,
    get_weight_projection,
    DailyNutritionLog,
    MealEntry
)


router = APIRouter()


def get_user_id(x_user_id: Optional[str] = Header(None, alias="X-User-ID")):
    """Dependency to extract X-User-ID header."""
    if not x_user_id:
        raise HTTPException(status_code=400, detail="X-User-ID header is required")
    return x_user_id


def serialize_meal_entry(meal: MealEntry) -> dict:
    """Convert MealEntry model to dict for response."""
    return {
        "id": meal.id,
        "user_id": meal.user_id,
        "date": meal.date.isoformat() if meal.date else None,
        "name": meal.name,
        "description": meal.name,  # Use name as description
        "calories": meal.calories,
        "protein": meal.protein,
        "carbs": meal.carbs,
        "fat": meal.fats,  # Map fats back to fat for API response
    }


def serialize_daily_log(daily_log: DailyNutritionLog) -> dict:
    """Convert DailyNutritionLog model to dict for response."""
    if daily_log is None:
        return None
    return {
        "id": daily_log.id,
        "user_id": daily_log.user_id,
        "date": daily_log.date.isoformat() if daily_log.date else None,
        "calories": daily_log.calories,
        "protein": daily_log.protein,
        "carbs": daily_log.carbs,
        "fats": daily_log.fats,
    }


@router.get("/{date}")
def get_nutrition_log(
    date: str,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    GET /api/v1/nutrition/{date}
    Get nutrition log for date (ISO YYYY-MM-DD) for X-User-ID
    """
    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in YYYY-MM-DD format")
    
    result = get_nutrition_log_by_date(db, user_id, date)
    
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    daily_log_dict = serialize_daily_log(result["daily_log"])
    meal_entries_list = [serialize_meal_entry(meal) for meal in result["meal_entries"]]
    
    return {
        "date": date,
        "daily_log": daily_log_dict,
        "meal_entries": meal_entries_list
    }


@router.post("/")
def create_nutrition_entry(
    meal_data: schemas.MealCreate,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    POST /api/v1/nutrition
    Create a nutrition log entry (manual): JSON body
    """
    # Override user_id from header
    meal_data.user_id = user_id
    
    meal = create_manual_meal_entry(db, meal_data)
    return serialize_meal_entry(meal)


@router.post("/upload")
async def upload_nutrition_image(
    file: UploadFile = File(...),
    date: Optional[str] = Form(None),
    save: Optional[bool] = Form(False),
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    POST /api/v1/nutrition/upload
    Upload image (multipart/form-data), backend forwards to Claude/Nutrition API 
    and returns estimated calories/protein/carbs/fats and saves log if requested
    """
    # Use current date if not provided
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in YYYY-MM-DD format")
    
    # Read file content
    contents = await file.read()
    
    # TODO: Forward to Claude/Nutrition API for analysis
    # For now, return placeholder estimate
    estimated_nutrition = {
        "calories": 500.0,
        "protein": 25.0,
        "carbs": 60.0,
        "fats": 18.0,
        "description": f"Estimated from {file.filename}"
    }
    
    # If save is requested, create meal entry
    if save:
        meal_data = schemas.MealCreate(
            user_id=user_id,
            date=date,
            calories=estimated_nutrition["calories"],
            protein=estimated_nutrition["protein"],
            carbs=estimated_nutrition["carbs"],
            fat=estimated_nutrition["fats"],
            description=estimated_nutrition["description"],
            img_url=None  # Could store S3 URL or path here
        )
        meal = create_manual_meal_entry(db, meal_data)
        estimated_nutrition["meal_id"] = meal.id
        estimated_nutrition["saved"] = True
    else:
        estimated_nutrition["saved"] = False
    
    return estimated_nutrition


@router.get("/projection")
def get_weight_projection_endpoint(
    user_id: str = Depends(get_user_id)
):
    """
    GET /api/v1/nutrition/projection
    Return weight projections (2w/1m/3m) based on history and settings (placeholder function)
    """
    projection = get_weight_projection(user_id)
    return {
        "two_weeks": projection["two_weeks"],
        "one_month": projection["one_month"],
        "three_months": projection["three_months"]
    }


@router.get("/daily-summary/{date}")
def get_daily_summary_endpoint(
    date: str,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    GET /api/v1/nutrition/daily-summary/{date}
    Quick summary for dashboard
    """
    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in YYYY-MM-DD format")
    
    summary = get_daily_summary(db, user_id, date)
    
    if summary is None:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    return summary