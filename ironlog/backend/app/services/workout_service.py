"""Workout service."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.workout import Set, WorkoutExercise, WorkoutSession
from app.schemas.workout import (
    QuickLogRequest,
    SetCreate,
    WorkoutExerciseCreate,
    WorkoutSessionCreate,
    WorkoutSessionUpdate,
)


def calculate_1rm(weight_kg: float, reps: int, rpe: float | None = None) -> float:
    """Calculate estimated 1RM using Epley formula with RPE adjustment."""
    if reps == 1:
        return weight_kg

    # Base Epley formula
    base_1rm = weight_kg * (1 + reps / 30.0)

    # RPE adjustment
    if rpe is not None:
        rir = 10 - rpe
        adjusted_reps = reps + rir
        base_1rm = weight_kg * (1 + adjusted_reps / 30.0)

    return round(base_1rm, 2)


async def detect_pr(
    db: AsyncSession, user_id: UUID, exercise_id: int, weight_kg: float, reps: int
) -> bool:
    """Detect if this set is a PR for the user."""
    query = (
        select(Set)
        .join(WorkoutExercise)
        .join(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutExercise.exercise_id == exercise_id,
            Set.weight_kg >= weight_kg,
            Set.reps >= reps,
        )
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    return existing is None


async def create_workout_session(
    db: AsyncSession, user_id: UUID, data: WorkoutSessionCreate
) -> WorkoutSession:
    """Create a new workout session."""
    session = WorkoutSession(
        user_id=user_id,
        started_at=data.started_at,
        session_name=data.session_name,
        notes=data.notes,
        bodyweight_kg=data.bodyweight_kg,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_workout_session(
    db: AsyncSession, session_id: UUID, user_id: UUID
) -> WorkoutSession | None:
    """Get workout session by ID."""
    query = (
        select(WorkoutSession)
        .where(WorkoutSession.id == session_id, WorkoutSession.user_id == user_id)
        .options(
            selectinload(WorkoutSession.exercises).selectinload(WorkoutExercise.sets)
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def list_workout_sessions(
    db: AsyncSession, user_id: UUID, limit: int = 50, offset: int = 0
) -> list[WorkoutSession]:
    """List workout sessions for a user."""
    query = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id)
        .options(
            selectinload(WorkoutSession.exercises).selectinload(WorkoutExercise.sets)
        )
        .order_by(WorkoutSession.started_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_workout_session(
    db: AsyncSession, session: WorkoutSession, data: WorkoutSessionUpdate
) -> WorkoutSession:
    """Update workout session."""
    if data.finished_at is not None:
        session.finished_at = data.finished_at
        if session.started_at:
            duration = (data.finished_at - session.started_at).total_seconds() / 60
            session.duration_minutes = int(duration)
    if data.session_name is not None:
        session.session_name = data.session_name
    if data.notes is not None:
        session.notes = data.notes
    if data.overall_rpe is not None:
        session.overall_rpe = data.overall_rpe
    if data.bodyweight_kg is not None:
        session.bodyweight_kg = data.bodyweight_kg

    await db.commit()
    await db.refresh(session)
    return session


async def delete_workout_session(
    db: AsyncSession, session: WorkoutSession
) -> None:
    """Delete workout session."""
    await db.delete(session)
    await db.commit()


async def add_exercise_to_session(
    db: AsyncSession, session_id: UUID, data: WorkoutExerciseCreate
) -> WorkoutExercise:
    """Add exercise to workout session."""
    workout_exercise = WorkoutExercise(
        session_id=session_id,
        exercise_id=data.exercise_id,
        user_exercise_id=data.user_exercise_id,
        exercise_order=data.exercise_order,
        notes=data.notes,
    )
    db.add(workout_exercise)
    await db.commit()
    await db.refresh(workout_exercise)
    return workout_exercise



async def add_set_to_exercise(
    db: AsyncSession,
    workout_exercise_id: int,
    user_id: UUID,
    exercise_id: int | None,
    data: SetCreate,
) -> Set:
    """Add set to workout exercise."""
    estimated_1rm = calculate_1rm(data.weight_kg, data.reps, data.rpe)

    is_pr = False
    if exercise_id:
        is_pr = await detect_pr(db, user_id, exercise_id, data.weight_kg, data.reps)

    set_obj = Set(
        workout_exercise_id=workout_exercise_id,
        set_order=data.set_order,
        set_type=data.set_type,
        weight_kg=data.weight_kg,
        reps=data.reps,
        rpe=data.rpe,
        rir=data.rir,
        is_pr=is_pr,
        estimated_1rm=estimated_1rm,
    )
    db.add(set_obj)
    await db.commit()
    await db.refresh(set_obj)

    # Update workout exercise totals
    await update_workout_exercise_totals(db, workout_exercise_id)

    return set_obj


async def update_workout_exercise_totals(
    db: AsyncSession, workout_exercise_id: int
) -> None:
    """Update totals for workout exercise."""
    query = select(WorkoutExercise).where(WorkoutExercise.id == workout_exercise_id)
    result = await db.execute(query)
    workout_exercise = result.scalar_one()

    sets_query = select(Set).where(Set.workout_exercise_id == workout_exercise_id)
    sets_result = await db.execute(sets_query)
    sets = list(sets_result.scalars().all())

    if sets:
        workout_exercise.total_volume_kg = sum(
            s.volume_kg for s in sets if s.volume_kg
        )
        max_1rm = max((s.estimated_1rm for s in sets if s.estimated_1rm), default=None)
        workout_exercise.estimated_1rm = max_1rm

    await db.commit()

    # Update session totals
    await update_session_totals(db, workout_exercise.session_id)


async def update_session_totals(db: AsyncSession, session_id: UUID) -> None:
    """Update totals for workout session."""
    query = (
        select(WorkoutSession)
        .where(WorkoutSession.id == session_id)
        .options(
            selectinload(WorkoutSession.exercises).selectinload(WorkoutExercise.sets)
        )
    )
    result = await db.execute(query)
    session = result.scalar_one()

    all_sets = [s for ex in session.exercises for s in ex.sets]
    session.total_sets = len(all_sets)
    session.total_volume_kg = sum(s.volume_kg for s in all_sets if s.volume_kg)

    await db.commit()


async def quick_log_workout(
    db: AsyncSession, user_id: UUID, data: QuickLogRequest
) -> WorkoutSession:
    """Quick log a workout with a single exercise."""
    session = WorkoutSession(
        user_id=user_id,
        started_at=datetime.utcnow(),
        finished_at=datetime.utcnow(),
        session_name=data.session_name,
        notes=data.notes,
        duration_minutes=0,
    )
    db.add(session)
    await db.flush()

    workout_exercise = WorkoutExercise(
        session_id=session.id,
        exercise_id=data.exercise_id,
        exercise_order=1,
    )
    db.add(workout_exercise)
    await db.flush()

    for set_data in data.sets:
        estimated_1rm = calculate_1rm(set_data.weight_kg, set_data.reps, set_data.rpe)
        is_pr = await detect_pr(
            db, user_id, data.exercise_id, set_data.weight_kg, set_data.reps
        )

        set_obj = Set(
            workout_exercise_id=workout_exercise.id,
            set_order=set_data.set_order,
            set_type=set_data.set_type,
            weight_kg=set_data.weight_kg,
            reps=set_data.reps,
            rpe=set_data.rpe,
            rir=set_data.rir,
            is_pr=is_pr,
            estimated_1rm=estimated_1rm,
        )
        db.add(set_obj)

    await db.commit()
    await db.refresh(session)

    # Update totals
    await update_workout_exercise_totals(db, workout_exercise.id)

    # Reload with relationships
    return await get_workout_session(db, session.id, user_id)
