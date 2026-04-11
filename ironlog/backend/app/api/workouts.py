"""Workout API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.workout import (
    QuickLogRequest,
    SetCreate,
    SetResponse,
    WorkoutExerciseCreate,
    WorkoutExerciseResponse,
    WorkoutSessionCreate,
    WorkoutSessionListResponse,
    WorkoutSessionResponse,
    WorkoutSessionResponseWrapper,
    WorkoutSessionUpdate,
)
from app.services import workout_service

router = APIRouter()


@router.post("/sessions", response_model=WorkoutSessionResponseWrapper)
async def create_session(
    data: WorkoutSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new workout session."""
    session = await workout_service.create_workout_session(
        db, current_user.id, data
    )
    return WorkoutSessionResponseWrapper(
        data=WorkoutSessionResponse.model_validate(session)
    )


@router.get("/sessions", response_model=WorkoutSessionListResponse)
async def list_sessions(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List workout sessions for current user."""
    sessions = await workout_service.list_workout_sessions(
        db, current_user.id, limit, offset
    )
    return WorkoutSessionListResponse(
        data=[WorkoutSessionResponse.model_validate(s) for s in sessions]
    )


@router.get("/sessions/{session_id}", response_model=WorkoutSessionResponseWrapper)
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get workout session by ID."""
    session = await workout_service.get_workout_session(
        db, session_id, current_user.id
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return WorkoutSessionResponseWrapper(
        data=WorkoutSessionResponse.model_validate(session)
    )


@router.patch("/sessions/{session_id}", response_model=WorkoutSessionResponseWrapper)
async def update_session(
    session_id: UUID,
    data: WorkoutSessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update workout session."""
    session = await workout_service.get_workout_session(
        db, session_id, current_user.id
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    updated_session = await workout_service.update_workout_session(db, session, data)
    return WorkoutSessionResponseWrapper(
        data=WorkoutSessionResponse.model_validate(updated_session)
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete workout session."""
    session = await workout_service.get_workout_session(
        db, session_id, current_user.id
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await workout_service.delete_workout_session(db, session)
    return {"data": {"message": "Session deleted"}, "error": None}


@router.post(
    "/sessions/{session_id}/exercises",
    response_model=dict,
)
async def add_exercise_to_session(
    session_id: UUID,
    data: WorkoutExerciseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add exercise to workout session."""
    session = await workout_service.get_workout_session(
        db, session_id, current_user.id
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    workout_exercise = await workout_service.add_exercise_to_session(
        db, session_id, data
    )
    return {
        "data": WorkoutExerciseResponse.model_validate(workout_exercise),
        "error": None,
    }


@router.post(
    "/exercises/{workout_exercise_id}/sets",
    response_model=dict,
)
async def add_set_to_exercise(
    workout_exercise_id: int,
    data: SetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add set to workout exercise."""
    # Verify ownership via session
    from app.models.workout import WorkoutExercise

    from sqlalchemy import select

    query = select(WorkoutExercise).where(WorkoutExercise.id == workout_exercise_id)
    result = await db.execute(query)
    workout_exercise = result.scalar_one_or_none()

    if not workout_exercise:
        raise HTTPException(status_code=404, detail="Workout exercise not found")

    session = await workout_service.get_workout_session(
        db, workout_exercise.session_id, current_user.id
    )
    if not session:
        raise HTTPException(status_code=403, detail="Not authorized")

    set_obj = await workout_service.add_set_to_exercise(
        db,
        workout_exercise_id,
        current_user.id,
        workout_exercise.exercise_id,
        data,
    )
    return {"data": SetResponse.model_validate(set_obj), "error": None}


@router.post("/quick-log", response_model=WorkoutSessionResponseWrapper)
async def quick_log(
    data: QuickLogRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Quick log a workout with a single exercise."""
    session = await workout_service.quick_log_workout(db, current_user.id, data)
    return WorkoutSessionResponseWrapper(
        data=WorkoutSessionResponse.model_validate(session)
    )
