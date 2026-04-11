"""Exercise schemas."""
from pydantic import BaseModel, Field


class MuscleGroupResponse(BaseModel):
    id: int
    name: str
    display_name: str
    body_region: str
    push_pull: str | None
    default_recovery_hours: int
    default_mrv_sets_week: int
    default_mev_sets_week: int

    class Config:
        from_attributes = True


class ExerciseMuscleResponse(BaseModel):
    muscle_group_id: int
    muscle_group_name: str
    role: str
    activation_pct: float

    class Config:
        from_attributes = True


class ExerciseSubstitutionResponse(BaseModel):
    id: int
    name: str
    display_name: str
    similarity: float
    reason: str | None

    class Config:
        from_attributes = True


class ExerciseResponse(BaseModel):
    id: int
    name: str
    display_name: str
    movement_pattern: str
    equipment: str
    is_compound: bool
    is_unilateral: bool
    supports_1rm: bool
    difficulty: str
    instructions: str | None
    tips: str | None
    common_mistakes: str | None
    muscles: list[ExerciseMuscleResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ExerciseDetailResponse(ExerciseResponse):
    substitutions: list[ExerciseSubstitutionResponse] = Field(
        default_factory=list
    )


class ExerciseListResponse(BaseModel):
    data: list[ExerciseResponse]
    error: None = None


class ExerciseDetailResponseWrapper(BaseModel):
    data: ExerciseDetailResponse | None
    error: dict | None = None


class MuscleGroupListResponse(BaseModel):
    data: list[MuscleGroupResponse]
    error: None = None
