"""Analytics schemas."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class VolumeDataResponse(BaseModel):
    """Weekly volume data for a muscle group."""
    
    muscle_group_id: int
    muscle_group_name: str
    total_sets: int
    total_volume_kg: float
    avg_rpe: float | None
    status: str
    mev: int
    mrv: int


class StrengthTimelineResponse(BaseModel):
    """Strength progression timeline point."""
    
    date: date
    actual_1rm: float | None
    predicted_1rm: float | None
    confidence_low: float | None
    confidence_high: float | None


class RecoveryStateResponse(BaseModel):
    """Recovery state for a muscle group."""
    
    muscle_group_id: int
    muscle_group_name: str
    fitness: float
    fatigue: float
    readiness: float
    fatigue_score: float
    estimated_recovery_pct: float


class ReadinessResponse(BaseModel):
    """Readiness score and recommendation."""
    
    readiness_score: float
    recommendation: str
    suggested_volume_adjustment: int
    recovery_pct: float
    fatigue_score: float


class WeightSuggestionResponse(BaseModel):
    """Weight suggestion for an exercise."""
    
    suggested_weight: float
    confidence: str
    adjustment_reason: str
    predicted_1rm: float
    readiness_score: float | None


class PlateauResponse(BaseModel):
    """Plateau detection."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    exercise_id: int
    detected_at: date
    plateau_start: date
    weeks_stalled: int
    estimated_1rm_at_plateau: float | None
    recommendation: str | None
    is_resolved: bool
    resolved_at: date | None


class TrainingInsightResponse(BaseModel):
    """Training insight."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    generated_at: datetime
    insight_type: str
    severity: str
    title: str
    body: str
    related_exercise_id: int | None
    related_muscle_group_id: int | None
    is_read: bool
    is_dismissed: bool
