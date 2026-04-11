"""Weekly analytics tasks."""
import asyncio
from datetime import date, datetime, timedelta

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.ml.autoregulation import AutoregulationEngine
from app.ml.volume_analyzer import VolumeAnalyzer
from app.models.analytics import TrainingInsight
from app.models.user import User
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.weekly.run_weekly_summary")
def run_weekly_summary():
    """
    Generate weekly training summary for all users.
    
    - Calculate weekly volume trends
    - Detect volume imbalances
    - Generate weekly insights
    - Check for deload recommendations
    """
    asyncio.run(_run_weekly_summary_async())


async def _run_weekly_summary_async():
    """Async implementation of weekly summary."""
    async with AsyncSessionLocal() as db:
        # Get all users
        users_query = select(User)
        users_result = await db.execute(users_query)
        users = list(users_result.scalars().all())

        for user in users:
            try:
                await _process_user_weekly(db, str(user.id))
            except Exception as e:
                print(f"Error processing weekly summary for user {user.id}: {e}")
                continue


async def _process_user_weekly(db, user_id: str):
    """Process weekly summary for a single user."""
    # 1. Detect volume imbalances
    volume_analyzer = VolumeAnalyzer(db)
    imbalances = await volume_analyzer.detect_imbalances(user_id, weeks=4)

    if imbalances:
        await _create_weekly_imbalance_insight(db, user_id, imbalances)

    # 2. Check for deload need
    autoregulation = AutoregulationEngine(db)
    deload_check = await autoregulation.detect_deload_need(user_id, weeks=4)

    if deload_check["needs_deload"] and deload_check["severity"] in ["medium", "high"]:
        await _create_deload_insight(db, user_id, deload_check)

    # 3. Generate weekly volume trend insight
    await _create_volume_trend_insight(db, user_id, volume_analyzer)


async def _create_weekly_imbalance_insight(db, user_id: str, imbalances: list):
    """Create weekly insight for volume imbalances."""
    if not imbalances:
        return

    # Focus on high severity imbalances
    high_severity = [i for i in imbalances if i["severity"] == "high"]

    if high_severity:
        muscle_names = ", ".join([i["muscle_group_name"] for i in high_severity[:3]])

        insight = TrainingInsight(
            user_id=user_id,
            generated_at=datetime.utcnow(),
            insight_type="imbalance",
            severity="warning",
            title="Weekly Review: Volume Imbalances Detected",
            body=(
                f"Over the past 4 weeks, these muscle groups have been undertrained: {muscle_names}. "
                "Consider adding 1-2 exercises per muscle group to bring volume into the optimal range."
            ),
        )
        db.add(insight)
        await db.commit()


async def _create_deload_insight(db, user_id: str, deload_check: dict):
    """Create insight recommending deload."""
    insight = TrainingInsight(
        user_id=user_id,
        generated_at=datetime.utcnow(),
        insight_type="recovery",
        severity="warning" if deload_check["severity"] == "high" else "info",
        title="Weekly Review: Deload Recommended",
        body=(
            f"{deload_check['recommendation']}\n\n"
            f"Reasons: {', '.join(deload_check['reasons'])}"
        ),
    )
    db.add(insight)
    await db.commit()


async def _create_volume_trend_insight(db, user_id: str, volume_analyzer: VolumeAnalyzer):
    """Create insight about weekly volume trends."""
    # Get current week and previous week volume
    current_week_start = _get_week_start(date.today())
    previous_week_start = current_week_start - timedelta(days=7)

    current_volume = await volume_analyzer.compute_weekly_volume(user_id, current_week_start)
    previous_volume = await volume_analyzer.compute_weekly_volume(user_id, previous_week_start)

    if not current_volume or not previous_volume:
        return

    # Calculate total sets
    current_total = sum(v["total_sets"] for v in current_volume)
    previous_total = sum(v["total_sets"] for v in previous_volume)

    if previous_total == 0:
        return

    change_pct = ((current_total - previous_total) / previous_total) * 100

    if abs(change_pct) > 20:
        direction = "increased" if change_pct > 0 else "decreased"
        insight = TrainingInsight(
            user_id=user_id,
            generated_at=datetime.utcnow(),
            insight_type="volume_warning" if abs(change_pct) > 30 else "recommendation",
            severity="warning" if abs(change_pct) > 30 else "info",
            title=f"Weekly Review: Volume {direction.capitalize()} by {abs(change_pct):.0f}%",
            body=(
                f"Your total training volume {direction} from {previous_total} to {current_total} sets this week. "
                f"{'Consider moderating volume increases to avoid overreaching.' if change_pct > 30 else ''}"
                f"{'Ensure this decrease is intentional (deload/recovery week).' if change_pct < -30 else ''}"
            ),
        )
        db.add(insight)
        await db.commit()


def _get_week_start(target_date: date) -> date:
    """Get Monday of the week containing target_date."""
    days_since_monday = target_date.weekday()
    return target_date - timedelta(days=days_since_monday)


@celery_app.task(name="app.tasks.weekly.detect_volume_imbalances")
def detect_volume_imbalances(user_id: str):
    """Detect muscle group volume imbalances for a user."""
    asyncio.run(_detect_volume_imbalances_async(user_id))


async def _detect_volume_imbalances_async(user_id: str):
    """Async implementation of volume imbalance detection."""
    async with AsyncSessionLocal() as db:
        volume_analyzer = VolumeAnalyzer(db)
        imbalances = await volume_analyzer.detect_imbalances(user_id, weeks=4)
        await _create_weekly_imbalance_insight(db, user_id, imbalances)


@celery_app.task(name="app.tasks.weekly.check_deload_needed")
def check_deload_needed(user_id: str):
    """Check if user needs a deload week."""
    asyncio.run(_check_deload_needed_async(user_id))


async def _check_deload_needed_async(user_id: str):
    """Async implementation of deload check."""
    async with AsyncSessionLocal() as db:
        autoregulation = AutoregulationEngine(db)
        deload_check = await autoregulation.detect_deload_need(user_id, weeks=4)

        if deload_check["needs_deload"]:
            await _create_deload_insight(db, user_id, deload_check)
