"""Recommendation service for training suggestions."""
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import MuscleGroupVolume, RecoveryState
from app.models.exercise import Exercise, MuscleGroup
from app.models.workout import WorkoutSession, Set, WorkoutExercise
from app.ml.autoregulation import AutoregulationEngine


async def recommend_weight(
    db: AsyncSession,
    user_id: UUID,
    exercise_id: int,
    target_reps: int = 8,
) -> dict:
    """Recommend weight for an exercise based on target reps."""
    engine = AutoregulationEngine(db)
    
    # Get recent sets for this exercise
    query = (
        select(Set)
        .join(WorkoutExercise)
        .join(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutExercise.exercise_id == exercise_id,
            WorkoutSession.finished_at.isnot(None),
        )
        .order_by(WorkoutSession.finished_at.desc())
        .limit(50)
    )
    result = await db.execute(query)
    sets = list(result.scalars().all())
    
    if not sets:
        return {
            "suggested_weight": None,
            "confidence": "low",
            "reason": "No training history for this exercise",
        }
    
    # Use autoregulation engine to suggest weight
    suggestion = await engine.suggest_weight(
        user_id=str(user_id),
        exercise_id=exercise_id,
        target_reps=target_reps,
        readiness_score=None,  # Could fetch from recovery state if needed
    )
    
    if not suggestion:
        # Fallback: use last set's weight
        last_set = sets[0]
        return {
            "suggested_weight": round(last_set.weight_kg, 1),
            "confidence": "medium",
            "reason": f"Based on last set ({last_set.weight_kg}kg × {last_set.reps} reps)",
        }
    
    return {
        "suggested_weight": suggestion["suggested_weight"],
        "confidence": suggestion["confidence"],
        "reason": suggestion["adjustment_reason"],
    }


async def recommend_exercises(
    db: AsyncSession,
    user_id: UUID,
    muscle_group: str | None = None,
    exclude_ids: list[int] | None = None,
    limit: int = 5,
) -> list[dict]:
    """Recommend exercises based on training history and muscle group."""
    # Get exercises for the muscle group
    query = select(Exercise)
    
    if muscle_group:
        query = query.join(Exercise.muscles).join(MuscleGroup).where(
            MuscleGroup.name == muscle_group
        )
    
    if exclude_ids:
        query = query.where(Exercise.id.notin_(exclude_ids))
    
    result = await db.execute(query)
    exercises = list(result.scalars().all())
    
    # Get user's training history to find underutilized exercises
    from sqlalchemy import func
    
    history_query = (
        select(WorkoutExercise.exercise_id, func.count(WorkoutExercise.id).label("count"))
        .join(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.finished_at >= datetime.utcnow() - timedelta(days=90),
        )
        .group_by(WorkoutExercise.exercise_id)
    )
    history_result = await db.execute(history_query)
    exercise_counts = {row[0]: row[1] for row in history_result.all()}
    
    # Score exercises (prefer less frequently used ones)
    scored_exercises = []
    for exercise in exercises:
        count = exercise_counts.get(exercise.id, 0)
        score = 1.0 / (count + 1)  # Lower count = higher score
        
        # Boost compound exercises
        if exercise.is_compound:
            score *= 1.5
        
        scored_exercises.append({
            "exercise_id": exercise.id,
            "exercise_name": exercise.display_name,
            "score": score,
            "times_used": count,
            "reason": f"{'Compound' if exercise.is_compound else 'Isolation'} exercise, used {count} times in last 90 days",
        })
    
    # Sort by score and return top N
    scored_exercises.sort(key=lambda x: x["score"], reverse=True)
    return scored_exercises[:limit]


async def check_deload_needed(
    db: AsyncSession,
    user_id: UUID,
) -> dict:
    """Check if user needs a deload week."""
    # Get volume trend for last 6 weeks
    six_weeks_ago = datetime.utcnow().date() - timedelta(weeks=6)
    
    query = (
        select(MuscleGroupVolume)
        .where(
            MuscleGroupVolume.user_id == user_id,
            MuscleGroupVolume.week_start >= six_weeks_ago,
        )
        .order_by(MuscleGroupVolume.week_start.asc())
    )
    result = await db.execute(query)
    volume_records = list(result.scalars().all())
    
    if len(volume_records) < 4:
        return {
            "deload_needed": False,
            "confidence": "low",
            "reason": "Insufficient training history (need at least 4 weeks)",
        }
    
    # Group by week and sum total sets
    weekly_volumes = {}
    for record in volume_records:
        week_key = record.week_start
        if week_key not in weekly_volumes:
            weekly_volumes[week_key] = 0
        weekly_volumes[week_key] += record.total_sets
    
    # Check for 4+ consecutive weeks of volume increase
    weeks = sorted(weekly_volumes.keys())
    consecutive_increases = 0
    
    for i in range(1, len(weeks)):
        if weekly_volumes[weeks[i]] > weekly_volumes[weeks[i-1]]:
            consecutive_increases += 1
        else:
            consecutive_increases = 0
    
    volume_increasing = consecutive_increases >= 3
    
    # Check recovery state
    recovery_query = (
        select(RecoveryState)
        .where(RecoveryState.user_id == user_id)
        .order_by(RecoveryState.computed_at.desc())
        .limit(10)
    )
    recovery_result = await db.execute(recovery_query)
    recovery_states = list(recovery_result.scalars().all())
    
    if not recovery_states:
        return {
            "deload_needed": volume_increasing,
            "confidence": "medium",
            "reason": "Volume has increased for 4+ weeks" if volume_increasing else "Volume stable",
            "prescription": "50% volume, maintain intensity, 1 week" if volume_increasing else None,
        }
    
    # Calculate average fatigue score
    avg_fatigue = sum(r.fatigue_score for r in recovery_states) / len(recovery_states)
    high_fatigue = avg_fatigue > 0.7
    
    deload_needed = volume_increasing and high_fatigue
    
    reason_parts = []
    if volume_increasing:
        reason_parts.append(f"Volume increased for {consecutive_increases + 1} consecutive weeks")
    if high_fatigue:
        reason_parts.append(f"High fatigue score ({avg_fatigue:.2f})")
    
    if not reason_parts:
        reason_parts.append("Training load is manageable")
    
    return {
        "deload_needed": deload_needed,
        "confidence": "high",
        "reason": "; ".join(reason_parts),
        "prescription": "50% volume, maintain intensity, 1 week" if deload_needed else None,
        "current_fatigue": round(avg_fatigue, 2),
        "volume_trend": "increasing" if volume_increasing else "stable",
    }


async def recommend_next_session(
    db: AsyncSession,
    user_id: UUID,
) -> dict:
    """Recommend next training session based on active program and recovery."""
    # Get active program
    from app.models.program import TrainingProgram
    from sqlalchemy.orm import selectinload
    
    query = (
        select(TrainingProgram)
        .where(
            TrainingProgram.user_id == user_id,
            TrainingProgram.is_active == True,
        )
        .options(selectinload(TrainingProgram.days))
    )
    result = await db.execute(query)
    program = result.scalar_one_or_none()
    
    if not program:
        return {
            "recommendation": "No active program",
            "suggested_day": None,
            "reason": "Create and activate a training program first",
        }
    
    # Get recovery state for muscle groups
    recovery_query = (
        select(RecoveryState)
        .where(RecoveryState.user_id == user_id)
        .order_by(RecoveryState.computed_at.desc())
    )
    recovery_result = await db.execute(recovery_query)
    recovery_states = list(recovery_result.scalars().all())
    
    # Find most recovered muscle groups
    recovery_by_muscle = {}
    for state in recovery_states:
        if state.muscle_group_id not in recovery_by_muscle:
            recovery_by_muscle[state.muscle_group_id] = state.estimated_recovery_pct
    
    # Find best day to train based on recovery
    best_day = None
    best_score = -1
    
    for day in program.days:
        # Calculate average recovery for this day's muscle groups
        if not day.target_muscle_groups:
            continue
        
        recoveries = [
            recovery_by_muscle.get(mg_id, 100)
            for mg_id in day.target_muscle_groups
        ]
        avg_recovery = sum(recoveries) / len(recoveries) if recoveries else 100
        
        if avg_recovery > best_score:
            best_score = avg_recovery
            best_day = day
    
    if not best_day:
        best_day = program.days[0] if program.days else None
    
    return {
        "recommendation": best_day.day_name if best_day else "Rest day",
        "suggested_day": best_day.day_number if best_day else None,
        "reason": f"Target muscle groups are {int(best_score)}% recovered" if best_day else "No program days configured",
        "recovery_score": round(best_score, 1) if best_day else None,
    }
