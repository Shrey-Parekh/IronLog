"""Nightly analytics tasks."""
import asyncio
from datetime import date, datetime, timedelta

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.ml.autoregulation import AutoregulationEngine
from app.ml.plateau_detector import PlateauDetector
from app.ml.recovery_model import BanisterRecoveryModel
from app.ml.strength_curve import StrengthCurveModel
from app.models.analytics import TrainingInsight
from app.models.user import User
from app.models.workout import WorkoutExercise, WorkoutSession
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.nightly.run_nightly_analytics")
def run_nightly_analytics():
    """
    Run nightly analytics for all users.
    
    - Retrain strength models
    - Recompute recovery states
    - Check for resolved plateaus
    - Detect inactivity
    - Generate readiness insights
    """
    asyncio.run(_run_nightly_analytics_async())


async def _run_nightly_analytics_async():
    """Async implementation of nightly analytics."""
    async with AsyncSessionLocal() as db:
        # Get all users
        users_query = select(User)
        users_result = await db.execute(users_query)
        users = list(users_result.scalars().all())

        for user in users:
            try:
                await _process_user_nightly(db, str(user.id))
            except Exception as e:
                print(f"Error processing user {user.id}: {e}")
                continue


async def _process_user_nightly(db, user_id: str):
    """Process nightly analytics for a single user."""
    # 1. Retrain strength models for active exercises
    await _retrain_user_models(db, user_id)

    # 2. Recompute recovery states
    recovery_model = BanisterRecoveryModel(db)
    recovery_states = await recovery_model.get_current_recovery_states(user_id)

    for state in recovery_states:
        await recovery_model.save_recovery_state(
            user_id, state["muscle_group_id"], state
        )

    # 3. Check for resolved plateaus
    await _check_resolved_plateaus(db, user_id)

    # 4. Check inactivity
    await _check_user_inactivity(db, user_id)

    # 5. Generate readiness insights
    await _generate_readiness_insights(db, user_id, recovery_states)


async def _retrain_user_models(db, user_id: str):
    """Retrain strength models for user's active exercises."""
    # Get exercises trained in last 90 days
    cutoff_date = datetime.utcnow() - timedelta(days=90)

    query = (
        select(WorkoutExercise.exercise_id)
        .join(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.started_at >= cutoff_date,
            WorkoutExercise.exercise_id.isnot(None),
        )
        .distinct()
    )
    result = await db.execute(query)
    exercise_ids = [row[0] for row in result.all()]

    # Retrain model for each exercise
    strength_model = StrengthCurveModel(db)
    for exercise_id in exercise_ids:
        historical_data = await strength_model.get_historical_data(
            user_id, exercise_id, days=90
        )

        if strength_model.fit(historical_data):
            await strength_model.save_estimate(user_id, exercise_id, date.today())


async def _check_resolved_plateaus(db, user_id: str):
    """Check if any plateaus have been resolved."""
    plateau_detector = PlateauDetector(db)
    active_plateaus = await plateau_detector.get_active_plateaus(user_id)

    for plateau in active_plateaus:
        is_resolved = await plateau_detector.check_resolved(
            user_id, plateau.exercise_id, plateau.plateau_start
        )

        if is_resolved:
            plateau.is_resolved = True
            plateau.resolved_at = date.today()

            # Create insight
            from app.models.exercise import Exercise

            ex_query = select(Exercise).where(Exercise.id == plateau.exercise_id)
            ex_result = await db.execute(ex_query)
            exercise = ex_result.scalar_one()

            insight = TrainingInsight(
                user_id=user_id,
                generated_at=datetime.utcnow(),
                insight_type="pr",
                severity="info",
                title=f"Plateau broken: {exercise.display_name}",
                body=(
                    f"Great work! Your {exercise.display_name} plateau has been resolved. "
                    f"You've shown consistent improvement over the past few weeks."
                ),
                related_exercise_id=plateau.exercise_id,
            )
            db.add(insight)

    await db.commit()


async def _check_user_inactivity(db, user_id: str):
    """Check for user inactivity and create reminder insight."""
    # Get last session
    query = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id)
        .order_by(WorkoutSession.started_at.desc())
        .limit(1)
    )
    result = await db.execute(query)
    last_session = result.scalar_one_or_none()

    if not last_session:
        return

    days_since_last = (datetime.utcnow() - last_session.started_at).days

    if days_since_last >= 7:
        # Check if we already sent a reminder recently
        recent_insight_query = select(TrainingInsight).where(
            TrainingInsight.user_id == user_id,
            TrainingInsight.insight_type == "recommendation",
            TrainingInsight.generated_at >= datetime.utcnow() - timedelta(days=3),
        )
        recent_result = await db.execute(recent_insight_query)
        recent_insight = recent_result.scalar_one_or_none()

        if not recent_insight:
            insight = TrainingInsight(
                user_id=user_id,
                generated_at=datetime.utcnow(),
                insight_type="recommendation",
                severity="info",
                title="Time to get back to training",
                body=(
                    f"It's been {days_since_last} days since your last workout. "
                    "Consistency is key for progress. Ready to start your next session?"
                ),
            )
            db.add(insight)
            await db.commit()


async def _generate_readiness_insights(db, user_id: str, recovery_states: list):
    """Generate insights about readiness and recovery."""
    if not recovery_states:
        return

    # Check for deload need
    autoregulation = AutoregulationEngine(db)
    deload_check = await autoregulation.detect_deload_need(user_id, weeks=4)

    if deload_check["needs_deload"]:
        insight = TrainingInsight(
            user_id=user_id,
            generated_at=datetime.utcnow(),
            insight_type="recovery",
            severity="warning" if deload_check["severity"] == "high" else "info",
            title="Consider a deload week",
            body=deload_check["recommendation"],
        )
        db.add(insight)
        await db.commit()


@celery_app.task(name="app.tasks.nightly.retrain_models")
def retrain_models(user_id: str):
    """Retrain ML models for a user."""
    asyncio.run(_retrain_models_async(user_id))


async def _retrain_models_async(user_id: str):
    """Async implementation of model retraining."""
    async with AsyncSessionLocal() as db:
        await _retrain_user_models(db, user_id)


@celery_app.task(name="app.tasks.nightly.check_inactivity")
def check_inactivity(user_id: str):
    """Check for user inactivity and send reminders."""
    asyncio.run(_check_inactivity_async(user_id))


async def _check_inactivity_async(user_id: str):
    """Async implementation of inactivity check."""
    async with AsyncSessionLocal() as db:
        await _check_user_inactivity(db, user_id)
