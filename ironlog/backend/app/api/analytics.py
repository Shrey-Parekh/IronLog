"""Analytics API endpoints."""
from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.ml.autoregulation import AutoregulationEngine
from app.ml.recovery_model import BanisterRecoveryModel
from app.ml.strength_curve import StrengthCurveModel
from app.ml.volume_analyzer import VolumeAnalyzer
from app.models.analytics import PlateauDetection, StrengthEstimate, TrainingInsight
from app.models.user import User
from app.schemas.analytics import (
    PlateauResponse,
    ReadinessResponse,
    RecoveryStateResponse,
    StrengthTimelineResponse,
    TrainingInsightResponse,
    VolumeDataResponse,
    WeightSuggestionResponse,
)

router = APIRouter(tags=["analytics"])


@router.get("/volume/weekly")
async def get_weekly_volume(
    weeks: int = Query(1, ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get weekly volume data for muscle groups."""
    volume_analyzer = VolumeAnalyzer(db)
    
    # Get current week start
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    volume_data = await volume_analyzer.compute_weekly_volume(
        str(current_user.id), week_start
    )
    
    return {"data": [VolumeDataResponse(**v) for v in volume_data], "error": None}


@router.get("/strength/{exercise_id}/timeline")
async def get_strength_timeline(
    exercise_id: int,
    days: int = Query(90, ge=30, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get strength progression timeline for an exercise."""
    strength_model = StrengthCurveModel(db)
    timeline = await strength_model.get_strength_timeline(
        str(current_user.id), exercise_id, days
    )
    
    return {
        "data": [StrengthTimelineResponse(**point) for point in timeline],
        "error": None,
    }


@router.get("/strength/{exercise_id}/current")
async def get_current_strength(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current strength estimate for an exercise."""
    query = (
        select(StrengthEstimate)
        .where(
            StrengthEstimate.user_id == current_user.id,
            StrengthEstimate.exercise_id == exercise_id,
        )
        .order_by(StrengthEstimate.estimated_at.desc())
        .limit(1)
    )
    result = await db.execute(query)
    estimate = result.scalar_one_or_none()
    
    if not estimate:
        return {"data": None, "error": {"code": "not_found", "message": "No strength data available"}}
    
    return {
        "data": {
            "estimated_1rm": float(estimate.estimated_1rm),
            "confidence_low": float(estimate.confidence_low) if estimate.confidence_low else None,
            "confidence_high": float(estimate.confidence_high) if estimate.confidence_high else None,
            "estimated_at": estimate.estimated_at,
            "data_points": estimate.data_points,
        },
        "error": None,
    }


@router.get("/recovery/states")
async def get_recovery_states(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current recovery states for all muscle groups."""
    recovery_model = BanisterRecoveryModel(db)
    states = await recovery_model.get_current_recovery_states(str(current_user.id))
    
    return {
        "data": [RecoveryStateResponse(**state) for state in states],
        "error": None,
    }


@router.get("/readiness/{muscle_group_id}")
async def get_readiness(
    muscle_group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get readiness score for a muscle group."""
    autoregulation = AutoregulationEngine(db)
    readiness = await autoregulation.compute_readiness(
        str(current_user.id), muscle_group_id
    )
    
    return {"data": ReadinessResponse(**readiness), "error": None}


@router.get("/weight-suggestion/{exercise_id}")
async def get_weight_suggestion(
    exercise_id: int,
    target_reps: int = Query(8, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get suggested weight for an exercise."""
    autoregulation = AutoregulationEngine(db)
    suggestion = await autoregulation.suggest_weight(
        str(current_user.id), exercise_id, target_reps
    )
    
    if not suggestion:
        return {
            "data": None,
            "error": {"code": "insufficient_data", "message": "Not enough training data for suggestion"},
        }
    
    return {"data": WeightSuggestionResponse(**suggestion), "error": None}


@router.get("/plateaus")
async def get_plateaus(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detected plateaus."""
    query = select(PlateauDetection).where(
        PlateauDetection.user_id == current_user.id
    )
    
    if active_only:
        query = query.where(PlateauDetection.is_resolved == False)
    
    query = query.order_by(PlateauDetection.detected_at.desc())
    
    result = await db.execute(query)
    plateaus = list(result.scalars().all())
    
    return {
        "data": [PlateauResponse.model_validate(p) for p in plateaus],
        "error": None,
    }


@router.get("/insights")
async def get_insights(
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get training insights."""
    query = (
        select(TrainingInsight)
        .where(
            TrainingInsight.user_id == current_user.id,
            TrainingInsight.is_dismissed == False,
        )
    )
    
    if unread_only:
        query = query.where(TrainingInsight.is_read == False)
    
    query = query.order_by(TrainingInsight.generated_at.desc()).limit(limit)
    
    result = await db.execute(query)
    insights = list(result.scalars().all())
    
    return {
        "data": [TrainingInsightResponse.model_validate(i) for i in insights],
        "error": None,
    }


@router.patch("/insights/{insight_id}/read")
async def mark_insight_read(
    insight_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an insight as read."""
    query = select(TrainingInsight).where(
        TrainingInsight.id == insight_id,
        TrainingInsight.user_id == current_user.id,
    )
    result = await db.execute(query)
    insight = result.scalar_one_or_none()
    
    if not insight:
        return {"data": None, "error": {"code": "not_found", "message": "Insight not found"}}
    
    insight.is_read = True
    await db.commit()
    
    return {"data": {"success": True}, "error": None}


@router.patch("/insights/{insight_id}/dismiss")
async def dismiss_insight(
    insight_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dismiss an insight."""
    query = select(TrainingInsight).where(
        TrainingInsight.id == insight_id,
        TrainingInsight.user_id == current_user.id,
    )
    result = await db.execute(query)
    insight = result.scalar_one_or_none()
    
    if not insight:
        return {"data": None, "error": {"code": "not_found", "message": "Insight not found"}}
    
    insight.is_dismissed = True
    await db.commit()
    
    return {"data": {"success": True}, "error": None}
