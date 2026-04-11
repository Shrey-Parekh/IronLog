"""Recovery modeling using Banister fitness-fatigue model."""
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import RecoveryState
from app.models.exercise import ExerciseMuscle, MuscleGroup
from app.models.workout import Set, WorkoutExercise, WorkoutSession


class BanisterRecoveryModel:
    """Models recovery using the Banister fitness-fatigue model."""

    # Default time constants (in days)
    TAU_FITNESS = 45.0  # Fitness decay time constant
    TAU_FATIGUE = 15.0  # Fatigue decay time constant

    # Default gain factors
    K_FITNESS = 1.0  # Fitness gain
    K_FATIGUE = 2.0  # Fatigue gain (higher = more fatiguing)

    def __init__(self, db: AsyncSession):
        self.db = db
        self.tau_fitness = self.TAU_FITNESS
        self.tau_fatigue = self.TAU_FATIGUE
        self.k_fitness = self.K_FITNESS
        self.k_fatigue = self.K_FATIGUE

    def compute_training_impulse(
        self, total_sets: int, avg_rpe: Optional[float], is_compound: bool
    ) -> float:
        """
        Compute training impulse (TRIMP) for a muscle group in a session.
        
        TRIMP = sets × RPE_factor × compound_multiplier
        """
        # Base impulse from set count
        impulse = float(total_sets)

        # RPE factor (6.0 = 1.0, 10.0 = 2.0)
        if avg_rpe:
            rpe_factor = 0.5 + (avg_rpe - 6.0) / 8.0  # Maps 6-10 to 0.5-1.0
            impulse *= rpe_factor

        # Compound exercises are more fatiguing
        if is_compound:
            impulse *= 1.3

        return impulse

    async def get_training_history(
        self, user_id: str, muscle_group_id: int, days: int = 60
    ) -> List[Dict]:
        """
        Get training history for a muscle group.
        
        Returns list of dicts with date, training_impulse.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get all sessions in period
        sessions_query = select(WorkoutSession).where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.started_at >= cutoff_date,
            WorkoutSession.finished_at.isnot(None),
        )
        sessions_result = await self.db.execute(sessions_query)
        sessions = list(sessions_result.scalars().all())

        if not sessions:
            return []

        session_ids = [s.id for s in sessions]

        # Get sets targeting this muscle group
        sets_query = (
            select(
                WorkoutSession.started_at,
                Set,
                ExerciseMuscle.role,
                ExerciseMuscle.activation_pct,
                WorkoutExercise.exercise_id,
            )
            .join(WorkoutExercise, Set.workout_exercise_id == WorkoutExercise.id)
            .join(WorkoutSession, WorkoutExercise.session_id == WorkoutSession.id)
            .join(ExerciseMuscle, WorkoutExercise.exercise_id == ExerciseMuscle.exercise_id)
            .where(
                WorkoutExercise.session_id.in_(session_ids),
                ExerciseMuscle.muscle_group_id == muscle_group_id,
            )
        )
        sets_result = await self.db.execute(sets_query)
        sets_data = list(sets_result.all())

        # Group by session date
        sessions_by_date: Dict[date, List] = {}
        for started_at, set_obj, role, activation_pct, exercise_id in sets_data:
            session_date = started_at.date()
            if session_date not in sessions_by_date:
                sessions_by_date[session_date] = []

            sessions_by_date[session_date].append({
                "set": set_obj,
                "role": role,
                "activation_pct": float(activation_pct),
                "exercise_id": exercise_id,
            })

        # Compute TRIMP for each session
        history = []
        for session_date, sets in sessions_by_date.items():
            # Count weighted sets
            total_sets = sum(
                1.0 if s["role"] == "primary" else s["activation_pct"]
                for s in sets
            )

            # Average RPE
            rpe_values = [float(s["set"].rpe) for s in sets if s["set"].rpe]
            avg_rpe = sum(rpe_values) / len(rpe_values) if rpe_values else None

            # Check if any compound exercises
            # (In real implementation, would query exercise table)
            is_compound = True  # Simplified assumption

            trimp = self.compute_training_impulse(int(total_sets), avg_rpe, is_compound)

            history.append({
                "date": session_date,
                "training_impulse": trimp,
            })

        return sorted(history, key=lambda x: x["date"])

    def compute_recovery_state(
        self, training_history: List[Dict], target_date: date
    ) -> Dict:
        """
        Compute fitness and fatigue at target date using Banister model.
        
        Returns dict with:
        - fitness: current fitness level
        - fatigue: current fatigue level
        - readiness: fitness - fatigue (performance potential)
        - fatigue_score: 0-1 normalized fatigue
        - estimated_recovery_pct: 0-100 recovery percentage
        """
        if not training_history:
            return {
                "fitness": 0.0,
                "fatigue": 0.0,
                "readiness": 0.0,
                "fatigue_score": 0.0,
                "estimated_recovery_pct": 100.0,
            }

        fitness = 0.0
        fatigue = 0.0

        for session in training_history:
            days_ago = (target_date - session["date"]).days
            if days_ago < 0:
                continue

            trimp = session["training_impulse"]

            # Exponential decay
            fitness += (
                self.k_fitness * trimp * np.exp(-days_ago / self.tau_fitness)
            )
            fatigue += (
                self.k_fatigue * trimp * np.exp(-days_ago / self.tau_fatigue)
            )

        readiness = fitness - fatigue

        # Normalize fatigue to 0-1 scale (assuming max fatigue ~20)
        fatigue_score = min(1.0, fatigue / 20.0)

        # Recovery percentage (inverse of fatigue)
        estimated_recovery_pct = max(0.0, min(100.0, (1.0 - fatigue_score) * 100))

        return {
            "fitness": round(fitness, 2),
            "fatigue": round(fatigue, 2),
            "readiness": round(readiness, 2),
            "fatigue_score": round(fatigue_score, 2),
            "estimated_recovery_pct": round(estimated_recovery_pct, 1),
        }

    def predict_readiness_at(
        self, training_history: List[Dict], future_date: date
    ) -> float:
        """Predict readiness at a future date."""
        state = self.compute_recovery_state(training_history, future_date)
        return state["readiness"]

    def personalize(
        self, training_history: List[Dict], performance_data: List[float]
    ) -> None:
        """
        Personalize model parameters based on user's response to training.
        
        This is a simplified version. Full implementation would use
        optimization to fit tau and k parameters to actual performance.
        """
        if len(training_history) < 10 or len(performance_data) < 10:
            return

        # Simplified: adjust based on average recovery time
        # Count days between sessions
        dates = [h["date"] for h in training_history]
        gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        avg_gap = sum(gaps) / len(gaps) if gaps else 3.0

        # Adjust fatigue decay based on typical recovery time
        if avg_gap < 2:
            # Trains frequently, likely recovers faster
            self.tau_fatigue = max(10.0, self.tau_fatigue * 0.9)
        elif avg_gap > 4:
            # Trains infrequently, may need more recovery
            self.tau_fatigue = min(20.0, self.tau_fatigue * 1.1)

    async def save_recovery_state(
        self, user_id: str, muscle_group_id: int, state: Dict
    ) -> None:
        """Save computed recovery state to database."""
        # Estimate when muscle will be ready (>80% recovered)
        if state["estimated_recovery_pct"] >= 80:
            next_ready_at = datetime.utcnow()
        else:
            # Estimate days until 80% recovered
            # Simplified: assume linear recovery
            days_needed = (80 - state["estimated_recovery_pct"]) / 10.0
            next_ready_at = datetime.utcnow() + timedelta(days=days_needed)

        # Get last trained date
        history = await self.get_training_history(user_id, muscle_group_id, days=30)
        last_trained_at = (
            datetime.combine(history[-1]["date"], datetime.min.time())
            if history
            else None
        )

        recovery_state = RecoveryState(
            user_id=user_id,
            muscle_group_id=muscle_group_id,
            computed_at=datetime.utcnow(),
            fatigue_score=state["fatigue_score"],
            estimated_recovery_pct=state["estimated_recovery_pct"],
            next_ready_at=next_ready_at,
            last_trained_at=last_trained_at,
        )

        self.db.add(recovery_state)
        await self.db.commit()

    async def get_current_recovery_states(
        self, user_id: str
    ) -> List[Dict]:
        """Get current recovery state for all trained muscle groups."""
        # Get all muscle groups
        muscle_groups_query = select(MuscleGroup)
        muscle_groups_result = await self.db.execute(muscle_groups_query)
        muscle_groups = list(muscle_groups_result.scalars().all())

        states = []
        for mg in muscle_groups:
            history = await self.get_training_history(user_id, mg.id, days=60)
            if not history:
                continue

            state = self.compute_recovery_state(history, date.today())
            state["muscle_group_id"] = mg.id
            state["muscle_group_name"] = mg.display_name
            states.append(state)

        return sorted(states, key=lambda x: x["estimated_recovery_pct"])
