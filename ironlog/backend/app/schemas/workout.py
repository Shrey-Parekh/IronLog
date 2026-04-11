"""Workout schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SetCreate(BaseModel):
    set_order: int
    set_type: str = "working"
    weight_kg: float
    reps: int
    rpe: float | None = None
    rir: int | None = None


class SetResponse(BaseModel):
    id: int
    set_order: int
    set_type: str
    weight_kg: float
    reps: int
    rpe: float | None
    rir: int | None
    is_pr: bool
    volume_kg: float | None
    estimated_1rm: float | None
    logged_at: datetime

    class Config:
        from_attributes = True


class WorkoutExerciseCreate(BaseModel):
    exercise_id: int | None = None
    user_exercise_id: int | None = None
    exercise_order: int
    notes: str | None = None


class WorkoutExerciseResponse(BaseModel):
    id: int
    exercise_id: int | None
    user_exercise_id: int | None
    exercise_order: int
    notes: str | None
    estimated_1rm: float | None
    total_volume_kg: float | None
    sets: list[SetResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class WorkoutSessionCreate(BaseModel):
    started_at: datetime
    session_name: str | None = None
    notes: str | None = None
    bodyweight_kg: float | None = None


class WorkoutSessionUpdate(BaseModel):
    finished_at: datetime | None = None
    session_name: str | None = None
    notes: str | None = None
    overall_rpe: float | None = None
    bodyweight_kg: float | None = None


class WorkoutSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    started_at: datetime
    finished_at: datetime | None
    session_name: str | None
    notes: str | None
    overall_rpe: float | None
    bodyweight_kg: float | None
    total_volume_kg: float | None
    total_sets: int | None
    duration_minutes: int | None
    created_at: datetime
    exercises: list[WorkoutExerciseResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class QuickLogRequest(BaseModel):
    exercise_id: int
    sets: list[SetCreate]
    session_name: str | None = None
    notes: str | None = None


class WorkoutSessionResponseWrapper(BaseModel):
    data: WorkoutSessionResponse | None
    error: dict | None = None


class WorkoutSessionListResponse(BaseModel):
    data: list[WorkoutSessionResponse]
    error: None = None
