"""Volume analyzer for tracking and analyzing training volume."""
from datetime import date, timedelta
from typing import Dict, List, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import MuscleGroupVolume
from app.models.exercise import ExerciseMuscle, MuscleGroup
from app.models.workout import Set, WorkoutExercise, WorkoutSession


class VolumeAnalyzer:
    """Analyzes training volume per muscle group."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def compute_weekly_volume(
        self, user_id: str, week_start: date
    ) -> List[Dict]:
        """
        Compute total volume per muscle group for a given week.
        
        Returns list of dicts with:
        - muscle_group_id
        - muscle_group_name
        - total_sets
        - total_volume_kg
        - avg_rpe
        - status (under_mev, in_range, over_mrv)
        """
        week_end = week_start + timedelta(days=7)

        # Get all sessions in the week
        sessions_query = select(WorkoutSession).where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.started_at >= week_start,
            WorkoutSession.started_at < week_end,
            WorkoutSession.finished_at.isnot(None),
        )
        sessions_result = await self.db.execute(sessions_query)
        sessions = list(sessions_result.scalars().all())

        if not sessions:
            return []

        session_ids = [s.id for s in sessions]

        # Get all sets from these sessions with exercise muscle data
        sets_query = (
            select(
                Set,
                ExerciseMuscle.muscle_group_id,
                ExerciseMuscle.role,
                ExerciseMuscle.activation_pct,
            )
            .join(WorkoutExercise, Set.workout_exercise_id == WorkoutExercise.id)
            .join(ExerciseMuscle, WorkoutExercise.exercise_id == ExerciseMuscle.exercise_id)
            .where(WorkoutExercise.session_id.in_(session_ids))
        )
        sets_result = await self.db.execute(sets_query)
        sets_data = list(sets_result.all())

        # Aggregate by muscle group
        muscle_volume: Dict[int, Dict] = {}

        for set_obj, muscle_group_id, role, activation_pct in sets_data:
            if muscle_group_id not in muscle_volume:
                muscle_volume[muscle_group_id] = {
                    "total_sets": 0,
                    "total_volume_kg": 0.0,
                    "rpe_sum": 0.0,
                    "rpe_count": 0,
                }

            # Weight sets by activation percentage and role
            set_weight = 1.0 if role == "primary" else float(activation_pct)

            muscle_volume[muscle_group_id]["total_sets"] += set_weight
            muscle_volume[muscle_group_id]["total_volume_kg"] += (
                float(set_obj.volume_kg or 0) * set_weight
            )

            if set_obj.rpe:
                muscle_volume[muscle_group_id]["rpe_sum"] += float(set_obj.rpe)
                muscle_volume[muscle_group_id]["rpe_count"] += 1

        # Get muscle group details and compute status
        muscle_groups_query = select(MuscleGroup).where(
            MuscleGroup.id.in_(muscle_volume.keys())
        )
        muscle_groups_result = await self.db.execute(muscle_groups_query)
        muscle_groups = {mg.id: mg for mg in muscle_groups_result.scalars().all()}

        results = []
        for mg_id, volume_data in muscle_volume.items():
            mg = muscle_groups.get(mg_id)
            if not mg:
                continue

            total_sets = int(volume_data["total_sets"])
            avg_rpe = (
                volume_data["rpe_sum"] / volume_data["rpe_count"]
                if volume_data["rpe_count"] > 0
                else None
            )

            # Determine status
            if total_sets < mg.default_mev_sets_week:
                status = "under_mev"
            elif total_sets > mg.default_mrv_sets_week:
                status = "over_mrv"
            else:
                status = "in_range"

            results.append({
                "muscle_group_id": mg_id,
                "muscle_group_name": mg.display_name,
                "total_sets": total_sets,
                "total_volume_kg": round(volume_data["total_volume_kg"], 2),
                "avg_rpe": round(avg_rpe, 1) if avg_rpe else None,
                "status": status,
                "mev": mg.default_mev_sets_week,
                "mrv": mg.default_mrv_sets_week,
            })

        return sorted(results, key=lambda x: x["total_sets"], reverse=True)

    async def save_weekly_volume(
        self, user_id: str, week_start: date, volume_data: List[Dict]
    ) -> None:
        """Save computed weekly volume to database."""
        for data in volume_data:
            volume_record = MuscleGroupVolume(
                user_id=user_id,
                muscle_group_id=data["muscle_group_id"],
                week_start=week_start,
                total_sets=data["total_sets"],
                total_volume_kg=data["total_volume_kg"],
                avg_rpe=data["avg_rpe"],
                status=data["status"],
            )
            self.db.add(volume_record)

        await self.db.commit()

    async def detect_imbalances(
        self, user_id: str, weeks: int = 4
    ) -> List[Dict]:
        """
        Detect muscle group imbalances over the last N weeks.
        
        Returns list of imbalances with:
        - muscle_group_name
        - avg_weekly_sets
        - expected_min_sets (MEV)
        - severity (low, medium, high)
        """
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks * 7)

        # Get volume data for the period
        volume_query = (
            select(
                MuscleGroupVolume.muscle_group_id,
                func.avg(MuscleGroupVolume.total_sets).label("avg_sets"),
            )
            .where(
                MuscleGroupVolume.user_id == user_id,
                MuscleGroupVolume.week_start >= start_date,
                MuscleGroupVolume.week_start < end_date,
            )
            .group_by(MuscleGroupVolume.muscle_group_id)
        )
        volume_result = await self.db.execute(volume_query)
        volume_by_muscle = {row[0]: float(row[1]) for row in volume_result.all()}

        # Get muscle group details
        muscle_groups_query = select(MuscleGroup)
        muscle_groups_result = await self.db.execute(muscle_groups_query)
        muscle_groups = list(muscle_groups_result.scalars().all())

        imbalances = []
        for mg in muscle_groups:
            avg_sets = volume_by_muscle.get(mg.id, 0.0)
            mev = mg.default_mev_sets_week

            if avg_sets < mev * 0.5:
                severity = "high"
            elif avg_sets < mev * 0.75:
                severity = "medium"
            elif avg_sets < mev:
                severity = "low"
            else:
                continue  # No imbalance

            imbalances.append({
                "muscle_group_id": mg.id,
                "muscle_group_name": mg.display_name,
                "avg_weekly_sets": round(avg_sets, 1),
                "expected_min_sets": mev,
                "deficit": round(mev - avg_sets, 1),
                "severity": severity,
            })

        return sorted(imbalances, key=lambda x: x["deficit"], reverse=True)

    async def weekly_volume_trend(
        self, user_id: str, muscle_group_id: int, weeks: int = 8
    ) -> List[Tuple[date, int]]:
        """
        Get weekly volume trend for a specific muscle group.
        
        Returns list of (week_start, total_sets) tuples.
        """
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks * 7)

        query = (
            select(MuscleGroupVolume.week_start, MuscleGroupVolume.total_sets)
            .where(
                MuscleGroupVolume.user_id == user_id,
                MuscleGroupVolume.muscle_group_id == muscle_group_id,
                MuscleGroupVolume.week_start >= start_date,
                MuscleGroupVolume.week_start < end_date,
            )
            .order_by(MuscleGroupVolume.week_start)
        )
        result = await self.db.execute(query)
        return [(row[0], row[1]) for row in result.all()]
