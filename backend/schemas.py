# schemas.py
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime, date


# -----------------------------
# USER CONFIG SCHEMAS
# -----------------------------

class UserConfigBase(BaseModel):
    age: int = Field(..., examples=[18])
    sex: str = Field(..., examples=["male"])
    height: float = Field(..., examples=[172.0])
    weight: float = Field(..., examples=[60.0])
    goal: str = Field(..., examples=["lose", "maintain", "gain"])
    activity: str | None = Field(default="moderate", examples=["low", "moderate", "high"])
    experience: str | None = Field(default="beginner", examples=["beginner", "intermediate", "advanced"])


class UserConfigCreate(UserConfigBase):
    user_id: str = Field(..., examples=["abc123xyz"])


class UserConfigResponse(UserConfigBase):
    user_id: str = Field(..., examples=["abc123xyz"])


class ExerciseBase(BaseModel):
    name: str = Field(..., examples=["Bench Press"])
    sets: int = Field(..., examples=[4])
    reps: int = Field(..., examples=[10])
    weight: float | None = Field(default=None, examples=[60.0])


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseResponse(ExerciseBase):
    id: int = Field(..., examples=[1])

class WorkoutSessionBase(BaseModel):
    day: str = Field(..., examples=["Monday"])
    name: str = Field(..., examples=["Chest Day"])
    exercises: List[ExerciseCreate] = Field(default_factory=list)


class WorkoutSessionCreate(WorkoutSessionBase):
    user_id: str = Field(..., examples=["abc123xyz"])


class WorkoutSessionResponse(WorkoutSessionBase):
    id: int = Field(..., examples=[12])
    user_id: str = Field(..., examples=["abc123xyz"])

class WorkoutHistoryBase(BaseModel):
    date: str = Field(..., examples=["2025-12-05"])
    completed_exercises: List[ExerciseCreate]


class WorkoutHistoryCreate(WorkoutHistoryBase):
    user_id: str = Field(..., examples=["abc123xyz"])


class WorkoutHistoryResponse(WorkoutHistoryBase):
    id: int = Field(..., examples=[99])
    user_id: str = Field(..., examples=["abc123xyz"])

class MealBase(BaseModel):
    img_url: str | None = Field(default=None, examples=["https://..."])
    calories: float = Field(..., examples=[520])
    protein: float = Field(..., examples=[30])
    carbs: float = Field(..., examples=[60])
    fat: float = Field(..., examples=[20])
    description: str | None = Field(default=None, examples=["Chicken rice"])


class MealCreate(MealBase):
    user_id: str = Field(..., examples=["abc123xyz"])
    date: str = Field(..., examples=["2025-12-05"])


class MealResponse(MealBase):
    id: int = Field(..., examples=[1])
    user_id: str = Field(..., examples=["abc123xyz"])
    date: str = Field(..., examples=["2025-12-05"])

class DashboardResponse(BaseModel):
    user_id: str = Field(..., examples=["abc123xyz"])
    streak_workout: int = Field(..., examples=[5])
    streak_nutrition: int = Field(..., examples=[3])
    estimated_weight_in_30_days: float = Field(..., examples=[58.5])
    today_calories: float = Field(..., examples=[1500])
    calorie_goal: float = Field(..., examples=[2000])
    motivational_quote: str = Field(..., examples=["Stay strong, stay consistent!"])


# -----------------------------
# NUTRITION SCHEMAS
# -----------------------------

class NutritionEstimateResponse(BaseModel):
    calories: float = Field(..., examples=[520])
    protein: float = Field(..., examples=[30])
    carbs: float = Field(..., examples=[60])
    fats: float = Field(..., examples=[20])
    description: str | None = Field(default=None, examples=["Chicken rice"])


class NutritionLogResponse(BaseModel):
    date: str = Field(..., examples=["2025-12-05"])
    daily_log: Optional[dict] = Field(default=None)
    meal_entries: List[dict] = Field(default_factory=list)


class DailySummaryResponse(BaseModel):
    date: str = Field(..., examples=["2025-12-05"])
    calories: float = Field(..., examples=[1500])
    protein: float = Field(..., examples=[80])
    carbs: float = Field(..., examples=[200])
    fats: float = Field(..., examples=[50])
    meal_count: int = Field(..., examples=[3])


class WeightProjectionResponse(BaseModel):
    two_weeks: Optional[float] = Field(default=None, examples=[58.5])
    one_month: Optional[float] = Field(default=None, examples=[58.0])
    three_months: Optional[float] = Field(default=None, examples=[57.0])

