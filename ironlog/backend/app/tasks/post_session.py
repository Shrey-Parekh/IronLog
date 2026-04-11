"""Post-session analytics tasks."""
import asyncio
from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.ml.plateau_detector import PlateauDetector
from app.ml.recovery_model import BanisterRecoveryModel
from app.ml.strength_curve import StrengthCurveModel
from app.ml.volume_analyzer import VolumeAnalyzer
from app.models.analytics import TrainingInsight
from app.models.exercise import ExerciseMuscle
from app.models.workout import WorkoutExercise, WorkoutSession
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.post_session.process_session_analytics")
def process_session_analytics(session_id: str, user_id: str):
    """
    Process analytics after a workout session is completed.
    
    9-step pipeline:
    1. Compute session totals
    2. Update 1RM estimates for all exercises
    3. Compute weekly volume
    4. Update recovery states
    5. Detect PRs
    6. Check for plateaus
    7. Detect volume imbalances
    8. Compute readiness scores
    9. Generate insights
    """
    asyncio.run(_process_session_analytics_async(session_id, user_id))


async def _process_session_analytics_async(session_id: str, user_id: str):
    """Async implementation of post-session analytics."""
    async with AsyncSessionLocal() as db:
        # Get session
        session_query = select(WorkoutSession).where(
            WorkoutSession.id == UUID(session_id)
        )
        session_result = await db.execute(session_query)
        session = session_result.scalar_one_or_none()

        if not session or not session.finished_at:
            return

        # Get all exercises in session
        exercises_query = select(WorkoutExercise).where(
            WorkoutExercise.session_id == UUID(session_id)
        )
        exercises_result = await db.execute(exercises_query)
        workout_exercises = list(exercises_result.scalars().all())

        # Step 1: Session totals (already computed in workout_service)

        # Step 2: Update 1RM estimates for each exercise
        strength_model = StrengthCurveModel(db)
        for we in workout_exercises:
            if we.exercise_id:
                await _update_1rm_estimate(
                    db, user_id, we.exercise_id, strength_model
                )

        # Step 3: Compute weekly volume
        volume_analyzer = VolumeAnalyzer(db)
        week_start = _get_week_start(session.started_at.date())
        volume_data = await volume_analyzer.compute_weekly_volume(user_id, week_start)
        await volume_analyzer.save_weekly_volume(user_id, week_start, volume_data)

        # Step 4: Update recovery states for trained muscle groups
        recovery_model = BanisterRecoveryModel(db)
        trained_muscle_groups = await _get_trained_muscle_groups(db, workout_exercises)
        for mg_id in trained_muscle_groups:
            history = await recovery_model.get_training_history(user_id, mg_id, days=60)
            state = recovery_model.compute_recovery_state(history, date.today())
            await recovery_model.save_recovery_state(user_id, mg_id, state)

        # Step 5: PRs already detected during set logging

        # Step 6: Check for plateaus
        plateau_detector = PlateauDetector(db)
        for we in workout_exercises:
            if we.exercise_id:
                await _check_plateau(db, user_id, we.exercise_id, plateau_detector)

        # Step 7: Detect volume imbalances
        imbalances = await volume_analyzer.detect_imbalances(user_id, weeks=4)
        if imbalances:
            await _create_imbalance_insights(db, user_id, imbalances)

        # Step 8 & 9: Readiness and insights handled by nightly job


async def _update_1rm_estimate(
    db, user_id: str, exercise_id: int, strength_model: StrengthCurveModel
):
    """Update 1RM estimate for an exercise."""
    historical_data = await strength_model.get_historical_data(
        user_id, exercise_id, days=90
    )

    if strength_model.fit(historical_data):
        await strength_model.save_estimate(user_id, exercise_id, date.today())


async def _get_trained_muscle_groups(db, workout_exercises: list) -> set:
    """Get unique muscle groups trained in session."""
    muscle_groups = set()

    for we in workout_exercises:
        if we.exercise_id:
            query = select(ExerciseMuscle.muscle_group_id).where(
                ExerciseMuscle.exercise_id == we.exercise_id
            )
            result = await db.execute(query)
            mg_ids = [row[0] for row in result.all()]
            muscle_groups.update(mg_ids)

    return muscle_groups


async def _check_plateau(
    db, user_id: str, exercise_id: int, plateau_detector: PlateauDetector
):
    """Check for plateau on an exercise."""
    strength_history = await plateau_detector.get_strength_history(
        user_id, exercise_id, days=180
    )

    plateau_info = plateau_detector.detect(strength_history)
    if plateau_info:
        # Check if already detected
        from app.models.analytics import PlateauDetection

        existing_query = select(PlateauDetection).where(
            PlateauDetection.user_id == user_id,
            PlateauDetection.exercise_id == exercise_id,
            PlateauDetection.is_resolved == False,
        )
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()

        if not existing:
            # Get exercise name
            from app.models.exercise import Exercise

            ex_query = select(Exercise).where(Exercise.id == exercise_id)
            ex_result = await db.execute(ex_query)
            exercise = ex_result.scalar_one()

            recommendation = plateau_detector.generate_recommendation(
                plateau_info, exercise.display_name
            )
            await plateau_detector.save_detection(
                user_id, exercise_id, plateau_info, recommendation
            )

            # Create insight
            insight = TrainingInsight(
                user_id=user_id,
                generated_at=datetime.utcnow(),
                insight_type="plateau",
                severity="warning",
                title=f"Plateau detected: {exercise.display_name}",
                body=recommendation,
                related_exercise_id=exercise_id,
            )
            db.add(insight)
            await db.commit()


async def _create_imbalance_insights(db, user_id: str, imbalances: list):
    """Create insights for volume imbalances."""
    for imbalance in imbalances[:3]:  # Top 3 imbalances
        if imbalance["severity"] in ["medium", "high"]:
            insight = TrainingInsight(
                user_id=user_id,
                generated_at=datetime.utcnow(),
                insight_type="imbalance",
                severity="warning" if imbalance["severity"] == "high" else "info",
                title=f"Low volume: {imbalance['muscle_group_name']}",
                body=(
                    f"Your {imbalance['muscle_group_name']} is receiving "
                    f"{imbalance['avg_weekly_sets']:.1f} sets per week, "
                    f"below the recommended minimum of {imbalance['expected_min_sets']} sets. "
                    f"Consider adding {int(imbalance['deficit'])} more sets per week."
                ),
                related_muscle_group_id=imbalance["muscle_group_id"],
            )
            db.add(insight)

    await db.commit()


def _get_week_start(target_date: date) -> date:
    """Get Monday of the week containing target_date."""
    days_since_monday = target_date.weekday()
    return target_date - timedelta(days=days_since_monday)


@celery_app.task(name="app.tasks.post_session.update_1rm_estimates")
def update_1rm_estimates(user_id: str, exercise_id: int):
    """Update 1RM estimates for an exercise."""
    asyncio.run(_update_1rm_estimates_async(user_id, exercise_id))


async def _update_1rm_estimates_async(user_id: str, exercise_id: int):
    """Async implementation of 1RM update."""
    async with AsyncSessionLocal() as db:
        strength_model = StrengthCurveModel(db)
        await _update_1rm_estimate(db, user_id, exercise_id, strength_model)


@celery_app.task(name="app.tasks.post_session.detect_prs")
def detect_prs(session_id: str, user_id: str):
    """Detect PRs in a completed session (already handled during set logging)."""
    # PRs are detected in real-time during set logging
    # This task is kept for potential batch processing
    pass
