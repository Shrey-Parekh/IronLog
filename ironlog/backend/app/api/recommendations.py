"""Recommendations API endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.services import recommendation_service

router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.get("/weight/{exercise_id}")
async def recommend_weight(
    exercise_id: int,
    target_reps: int = Query(default=8, ge=1, le=30),
    target_rpe: float = Query(default=8.0, ge=6.0, le=10.0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Recommend weight for an exercise based on target reps and RPE."""
    result = await recommendation_service.recommend_weight(
        db=db,
        user_id=current_user.id,
        exercise_id=exercise_id,
        target_reps=target_reps,
        target_rpe=target_rpe,
    )
    return result


@router.get("/exercises")
async def recommend_exercises(
    muscle_group: str | None = Query(default=None),
    exclude_ids: str | None = Query(default=None, description="Comma-separated exercise IDs to exclude"),
    limit: int = Query(default=5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Recommend exercises based on training history and muscle group."""
    exclude_list = []
    if exclude_ids:
        try:
            exclude_list = [int(x.strip()) for x in exclude_ids.split(",")]
        except ValueError:
            pass
    
    result = await recommendation_service.recommend_exercises(
        db=db,
        user_id=current_user.id,
        muscle_group=muscle_group,
        exclude_ids=exclude_list if exclude_list else None,
        limit=limit,
    )
    return {"recommendations": result}


@router.get("/deload")
async def check_deload(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if user needs a deload week."""
    result = await recommendation_service.check_deload_needed(
        db=db,
        user_id=current_user.id,
    )
    return result


@router.get("/next-session")
async def recommend_next_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Recommend next training session based on active program and recovery."""
    result = await recommendation_service.recommend_next_session(
        db=db,
        user_id=current_user.id,
    )
    return result
