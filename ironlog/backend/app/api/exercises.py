"""Exercise API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.exercise import (
    ExerciseDetailResponse,
    ExerciseDetailResponseWrapper,
    ExerciseListResponse,
    ExerciseMuscleResponse,
    ExerciseResponse,
    ExerciseSubstitutionResponse,
    MuscleGroupListResponse,
    MuscleGroupResponse,
)
from app.services import exercise_service

router = APIRouter()


@router.get("/exercises", response_model=ExerciseListResponse)
async def list_exercises(
    equipment: str | None = Query(None),
    movement_pattern: str | None = Query(None),
    muscle_group_id: int | None = Query(None),
    is_compound: bool | None = Query(None),
    difficulty: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all exercises with optional filters."""
    exercises = await exercise_service.get_all_exercises(
        db,
        equipment=equipment,
        movement_pattern=movement_pattern,
        muscle_group_id=muscle_group_id,
        is_compound=is_compound,
        difficulty=difficulty,
    )

    return ExerciseListResponse(
        data=[
            ExerciseResponse(
                id=ex.id,
                name=ex.name,
                display_name=ex.display_name,
                movement_pattern=ex.movement_pattern,
                equipment=ex.equipment,
                is_compound=ex.is_compound,
                is_unilateral=ex.is_unilateral,
                supports_1rm=ex.supports_1rm,
                difficulty=ex.difficulty,
                instructions=ex.instructions,
                tips=ex.tips,
                common_mistakes=ex.common_mistakes,
                muscles=[
                    ExerciseMuscleResponse(
                        muscle_group_id=em.muscle_group_id,
                        muscle_group_name=em.muscle_group.name,
                        role=em.role,
                        activation_pct=float(em.activation_pct),
                    )
                    for em in ex.muscles
                ],
            )
            for ex in exercises
        ]
    )


@router.get("/exercises/search", response_model=ExerciseListResponse)
async def search_exercises(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    """Search exercises by name."""
    exercises = await exercise_service.search_exercises(db, q)

    return ExerciseListResponse(
        data=[
            ExerciseResponse(
                id=ex.id,
                name=ex.name,
                display_name=ex.display_name,
                movement_pattern=ex.movement_pattern,
                equipment=ex.equipment,
                is_compound=ex.is_compound,
                is_unilateral=ex.is_unilateral,
                supports_1rm=ex.supports_1rm,
                difficulty=ex.difficulty,
                instructions=ex.instructions,
                tips=ex.tips,
                common_mistakes=ex.common_mistakes,
                muscles=[
                    ExerciseMuscleResponse(
                        muscle_group_id=em.muscle_group_id,
                        muscle_group_name=em.muscle_group.name,
                        role=em.role,
                        activation_pct=float(em.activation_pct),
                    )
                    for em in ex.muscles
                ],
            )
            for ex in exercises
        ]
    )


@router.get("/exercises/{exercise_id}", response_model=ExerciseDetailResponseWrapper)
async def get_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get exercise by ID."""
    exercise = await exercise_service.get_exercise_by_id(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    substitutions_data = await exercise_service.get_exercise_substitutions(
        db, exercise_id
    )

    return ExerciseDetailResponseWrapper(
        data=ExerciseDetailResponse(
            id=exercise.id,
            name=exercise.name,
            display_name=exercise.display_name,
            movement_pattern=exercise.movement_pattern,
            equipment=exercise.equipment,
            is_compound=exercise.is_compound,
            is_unilateral=exercise.is_unilateral,
            supports_1rm=exercise.supports_1rm,
            difficulty=exercise.difficulty,
            instructions=exercise.instructions,
            tips=exercise.tips,
            common_mistakes=exercise.common_mistakes,
            muscles=[
                ExerciseMuscleResponse(
                    muscle_group_id=em.muscle_group_id,
                    muscle_group_name=em.muscle_group.name,
                    role=em.role,
                    activation_pct=float(em.activation_pct),
                )
                for em in exercise.muscles
            ],
            substitutions=[
                ExerciseSubstitutionResponse(
                    id=sub_ex.id,
                    name=sub_ex.name,
                    display_name=sub_ex.display_name,
                    similarity=float(similarity),
                    reason=reason,
                )
                for sub_ex, similarity, reason in substitutions_data
            ],
        )
    )


@router.get(
    "/exercises/{exercise_id}/substitutions",
    response_model=ExerciseListResponse,
)
async def get_exercise_substitutions(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get substitutions for an exercise."""
    substitutions_data = await exercise_service.get_exercise_substitutions(
        db, exercise_id
    )

    return ExerciseListResponse(
        data=[
            ExerciseResponse(
                id=sub_ex.id,
                name=sub_ex.name,
                display_name=sub_ex.display_name,
                movement_pattern=sub_ex.movement_pattern,
                equipment=sub_ex.equipment,
                is_compound=sub_ex.is_compound,
                is_unilateral=sub_ex.is_unilateral,
                supports_1rm=sub_ex.supports_1rm,
                difficulty=sub_ex.difficulty,
                instructions=sub_ex.instructions,
                tips=sub_ex.tips,
                common_mistakes=sub_ex.common_mistakes,
                muscles=[
                    ExerciseMuscleResponse(
                        muscle_group_id=em.muscle_group_id,
                        muscle_group_name=em.muscle_group.name,
                        role=em.role,
                        activation_pct=float(em.activation_pct),
                    )
                    for em in sub_ex.muscles
                ],
            )
            for sub_ex, _, _ in substitutions_data
        ]
    )


@router.get("/muscle-groups", response_model=MuscleGroupListResponse)
async def list_muscle_groups(
    db: AsyncSession = Depends(get_db),
):
    """List all muscle groups."""
    muscle_groups = await exercise_service.get_all_muscle_groups(db)

    return MuscleGroupListResponse(
        data=[
            MuscleGroupResponse(
                id=mg.id,
                name=mg.name,
                display_name=mg.display_name,
                body_region=mg.body_region,
                push_pull=mg.push_pull,
                default_recovery_hours=mg.default_recovery_hours,
                default_mrv_sets_week=mg.default_mrv_sets_week,
                default_mev_sets_week=mg.default_mev_sets_week,
            )
            for mg in muscle_groups
        ]
    )


@router.get(
    "/muscle-groups/{muscle_group_id}/exercises",
    response_model=ExerciseListResponse,
)
async def get_exercises_by_muscle_group(
    muscle_group_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get exercises that target a specific muscle group."""
    exercises = await exercise_service.get_exercises_by_muscle_group(
        db, muscle_group_id
    )

    return ExerciseListResponse(
        data=[
            ExerciseResponse(
                id=ex.id,
                name=ex.name,
                display_name=ex.display_name,
                movement_pattern=ex.movement_pattern,
                equipment=ex.equipment,
                is_compound=ex.is_compound,
                is_unilateral=ex.is_unilateral,
                supports_1rm=ex.supports_1rm,
                difficulty=ex.difficulty,
                instructions=ex.instructions,
                tips=ex.tips,
                common_mistakes=ex.common_mistakes,
                muscles=[
                    ExerciseMuscleResponse(
                        muscle_group_id=em.muscle_group_id,
                        muscle_group_name=em.muscle_group.name,
                        role=em.role,
                        activation_pct=float(em.activation_pct),
                    )
                    for em in ex.muscles
                ],
            )
            for ex in exercises
        ]
    )
