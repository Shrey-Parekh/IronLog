"""Program schemas."""
from pydantic import BaseModel, Field


class ProgramDayResponse(BaseModel):
    """Program day response."""
    id: int
    day_number: int
    day_name: str
    target_muscle_groups: list[int]
    
    class Config:
        from_attributes = True


class TrainingProgramResponse(BaseModel):
    """Training program response."""
    id: int
    user_id: str
    name: str
    days_per_week: int
    is_active: bool
    days: list[ProgramDayResponse] = []
    
    class Config:
        from_attributes = True


class GenerateSplitRequest(BaseModel):
    """Request to generate a training split."""
    days_per_week: int = Field(ge=2, le=7, description="Number of training days per week")
    session_duration_minutes: int = Field(ge=30, le=180, default=60, description="Target session duration")
    goal: str = Field(description="Training goal: strength, hypertrophy, or balanced")
    experience_level: str = Field(default="intermediate", description="beginner, intermediate, or advanced")
    exclude_muscle_groups: list[int] = Field(default_factory=list, description="Muscle group IDs to exclude")


class GenerateSplitResponse(BaseModel):
    """Generated training split response."""
    program: TrainingProgramResponse
    rationale: str = Field(description="Explanation of the split design")
    estimated_volume_per_muscle: dict[str, int] = Field(description="Estimated weekly sets per muscle group")


class ExerciseRecommendation(BaseModel):
    """Exercise recommendation."""
    exercise_id: int
    exercise_name: str
    sets: int
    reps_range: str
    reason: str
