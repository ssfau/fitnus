from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Form
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import base64
import os
import json
from anthropic import Anthropic

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
    user_id: str = Form(...),
    date: str = Form(None),
    save: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Upload a food image → send to Claude → get nutrition estimates → save meal if requested.
    """

    # 1️⃣ Validate date
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be YYYY-MM-DD")

    # 2️⃣ Read file
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Image file is empty")

    # Convert image to base64
    image_base64 = base64.b64encode(contents).decode("utf-8")

    # Determine MIME type from uploaded file
    mime_type = file.content_type

    # 3️⃣ Initialize Claude client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set")

    client = Anthropic(api_key=api_key)

    # 4️⃣ Prompt
    prompt = """
You are a nutrition estimation model. Analyze the provided food image and return ONLY a JSON object
with this structure:

{
  "calories": <number>,
  "protein": <grams>,
  "carbs": <grams>,
  "fats": <grams>,
  "description": "<short description of the meal>"
}

Make your best nutritional estimate. No extra commentary.
"""

    # 5️⃣ Claude API call
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[
    {
        "role": "user",
        "content": [
            {
                "type": "image",             # ✅ correct type
                "source": {
                    "type": "base64",
                    "data": image_base64,
                    "media_type": mime_type  # e.g., "image/jpeg"
                }
            },
            {"type": "text", "text": prompt}
        ]
    }
    ]
        )

        response_text = message.content[0].text

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")

    # 6️⃣ Extract JSON from Claude response
    try:
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1

        if json_start == -1 or json_end == -1:
            raise ValueError("Claude returned no JSON")

        nutrition_data = json.loads(response_text[json_start:json_end])

    except Exception:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse JSON from Claude response: {response_text}"
        )

    # 7️⃣ Validate + structure response
    estimated = {
        "calories": float(nutrition_data.get("calories", 0)),
        "protein": float(nutrition_data.get("protein", 0)),
        "carbs": float(nutrition_data.get("carbs", 0)),
        "fats": float(nutrition_data.get("fats", 0)),
        "description": nutrition_data.get("description", "Unknown meal"),
    }

    # 8️⃣ Optional: save to DB
    if save:
        meal_data = schemas.MealCreate(
            user_id=user_id,
            date=date,
            calories=estimated["calories"],
            protein=estimated["protein"],
            carbs=estimated["carbs"],
            fat=estimated["fats"],
            description=estimated["description"],
            img_url=None
        )

        meal = create_manual_meal_entry(db, meal_data)
        estimated["meal_id"] = meal.id
        estimated["saved"] = True
    else:
        estimated["saved"] = False

    return estimated


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