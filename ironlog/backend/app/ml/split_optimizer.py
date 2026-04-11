"""Training split optimizer for generating personalized programs."""
from datetime import date
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise import Exercise, ExerciseMuscle, MuscleGroup
from app.models.user import User


class SplitOptimizer:
    """Generates optimized training splits based on recovery and goals."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_split(
        self,
        user_id: str,
        days_per_week: int,
        goal: str = "hypertrophy",
        experience_level: str = "intermediate",
    ) -> Dict:
        """
        Generate an optimized training split.
        
        Args:
            days_per_week: 3-6 training days
            goal: "strength", "hypertrophy", or "endurance"
            experience_level: "beginner", "intermediate", "advanced"
            
        Returns dict with:
        - split_type: str (e.g., "upper_lower", "push_pull_legs")
        - days: list of day configs
        - rationale: str
        """
        # Get user info
        user_query = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        # Get all muscle groups
        muscle_groups_query = select(MuscleGroup)
        muscle_groups_result = await self.db.execute(muscle_groups_query)
        muscle_groups = list(muscle_groups_result.scalars().all())

        # Determine split type based on frequency
        if days_per_week <= 3:
            split_type = "full_body"
            days = await self._generate_full_body_split(
                muscle_groups, days_per_week, goal
            )
        elif days_per_week == 4:
            split_type = "upper_lower"
            days = await self._generate_upper_lower_split(
                muscle_groups, goal
            )
        elif days_per_week == 5:
            split_type = "push_pull_legs"
            days = await self._generate_ppl_split(muscle_groups, goal)
        else:  # 6 days
            split_type = "push_pull_legs_x2"
            days = await self._generate_ppl_split(muscle_groups, goal)
            days = days + days  # Repeat for 6 days

        rationale = self._generate_rationale(
            split_type, days_per_week, goal, experience_level
        )

        return {
            "split_type": split_type,
            "days_per_week": days_per_week,
            "days": days,
            "rationale": rationale,
        }

    async def _generate_full_body_split(
        self, muscle_groups: List[MuscleGroup], days: int, goal: str
    ) -> List[Dict]:
        """Generate full body split (all muscle groups each session)."""
        # Group muscle groups by region
        upper = [mg for mg in muscle_groups if mg.body_region == "upper"]
        lower = [mg for mg in muscle_groups if mg.body_region == "lower"]
        core = [mg for mg in muscle_groups if mg.body_region == "core"]

        # Get exercises for each muscle group
        exercises_by_mg = await self._get_exercises_by_muscle_groups(
            [mg.id for mg in muscle_groups]
        )

        split_days = []
        for day_num in range(1, days + 1):
            day_exercises = []

            # Add compound movements first
            day_exercises.extend(
                await self._select_exercises(
                    exercises_by_mg, upper[:3], 1, is_compound=True
                )
            )
            day_exercises.extend(
                await self._select_exercises(
                    exercises_by_mg, lower[:2], 1, is_compound=True
                )
            )

            # Add isolation work
            day_exercises.extend(
                await self._select_exercises(
                    exercises_by_mg, upper[3:], 1, is_compound=False
                )
            )

            split_days.append({
                "day_number": day_num,
                "day_name": f"Full Body {chr(64 + day_num)}",
                "target_muscle_groups": [mg.id for mg in muscle_groups],
                "exercises": day_exercises,
                "estimated_duration_minutes": 60,
            })

        return split_days

    async def _generate_upper_lower_split(
        self, muscle_groups: List[MuscleGroup], goal: str
    ) -> List[Dict]:
        """Generate upper/lower split."""
        upper = [mg for mg in muscle_groups if mg.body_region == "upper"]
        lower = [mg for mg in muscle_groups if mg.body_region == "lower"]

        exercises_by_mg = await self._get_exercises_by_muscle_groups(
            [mg.id for mg in muscle_groups]
        )

        return [
            {
                "day_number": 1,
                "day_name": "Upper A",
                "target_muscle_groups": [mg.id for mg in upper],
                "exercises": await self._select_exercises(
                    exercises_by_mg, upper, 2, is_compound=True
                ),
                "estimated_duration_minutes": 60,
            },
            {
                "day_number": 2,
                "day_name": "Lower A",
                "target_muscle_groups": [mg.id for mg in lower],
                "exercises": await self._select_exercises(
                    exercises_by_mg, lower, 2, is_compound=True
                ),
                "estimated_duration_minutes": 60,
            },
            {
                "day_number": 3,
                "day_name": "Upper B",
                "target_muscle_groups": [mg.id for mg in upper],
                "exercises": await self._select_exercises(
                    exercises_by_mg, upper, 2, is_compound=False
                ),
                "estimated_duration_minutes": 60,
            },
            {
                "day_number": 4,
                "day_name": "Lower B",
                "target_muscle_groups": [mg.id for mg in lower],
                "exercises": await self._select_exercises(
                    exercises_by_mg, lower, 2, is_compound=False
                ),
                "estimated_duration_minutes": 60,
            },
        ]

    async def _generate_ppl_split(
        self, muscle_groups: List[MuscleGroup], goal: str
    ) -> List[Dict]:
        """Generate push/pull/legs split."""
        push = [mg for mg in muscle_groups if mg.push_pull == "push"]
        pull = [mg for mg in muscle_groups if mg.push_pull == "pull"]
        legs = [mg for mg in muscle_groups if mg.body_region == "lower"]

        exercises_by_mg = await self._get_exercises_by_muscle_groups(
            [mg.id for mg in muscle_groups]
        )

        return [
            {
                "day_number": 1,
                "day_name": "Push",
                "target_muscle_groups": [mg.id for mg in push],
                "exercises": await self._select_exercises(
                    exercises_by_mg, push, 2
                ),
                "estimated_duration_minutes": 60,
            },
            {
                "day_number": 2,
                "day_name": "Pull",
                "target_muscle_groups": [mg.id for mg in pull],
                "exercises": await self._select_exercises(
                    exercises_by_mg, pull, 2
                ),
                "estimated_duration_minutes": 60,
            },
            {
                "day_number": 3,
                "day_name": "Legs",
                "target_muscle_groups": [mg.id for mg in legs],
                "exercises": await self._select_exercises(
                    exercises_by_mg, legs, 2
                ),
                "estimated_duration_minutes": 60,
            },
        ]

    async def _get_exercises_by_muscle_groups(
        self, muscle_group_ids: List[int]
    ) -> Dict[int, List[Exercise]]:
        """Get exercises grouped by muscle group."""
        query = (
            select(Exercise, ExerciseMuscle.muscle_group_id)
            .join(ExerciseMuscle)
            .where(
                ExerciseMuscle.muscle_group_id.in_(muscle_group_ids),
                ExerciseMuscle.role == "primary",
            )
        )
        result = await self.db.execute(query)
        rows = list(result.all())

        exercises_by_mg: Dict[int, List[Exercise]] = {}
        for exercise, mg_id in rows:
            if mg_id not in exercises_by_mg:
                exercises_by_mg[mg_id] = []
            exercises_by_mg[mg_id].append(exercise)

        return exercises_by_mg

    async def _select_exercises(
        self,
        exercises_by_mg: Dict[int, List[Exercise]],
        muscle_groups: List[MuscleGroup],
        count_per_group: int,
        is_compound: Optional[bool] = None,
    ) -> List[Dict]:
        """Select exercises for muscle groups."""
        selected = []

        for mg in muscle_groups:
            exercises = exercises_by_mg.get(mg.id, [])

            # Filter by compound if specified
            if is_compound is not None:
                exercises = [e for e in exercises if e.is_compound == is_compound]

            # Take first N exercises (in real implementation, would be smarter)
            for exercise in exercises[:count_per_group]:
                selected.append({
                    "exercise_id": exercise.id,
                    "exercise_name": exercise.display_name,
                    "target_sets": 3,
                    "target_reps_min": 8,
                    "target_reps_max": 12,
                })

        return selected

    def _generate_rationale(
        self, split_type: str, days: int, goal: str, experience: str
    ) -> str:
        """Generate explanation for the split."""
        rationales = {
            "full_body": (
                f"Full body training {days}x per week is ideal for {experience} lifters "
                f"focusing on {goal}. Each muscle group is trained {days}x per week "
                "with adequate recovery between sessions."
            ),
            "upper_lower": (
                f"Upper/lower split allows you to train each muscle group 2x per week "
                f"with {days} training days. This frequency is optimal for {goal} "
                f"while providing sufficient recovery for {experience} lifters."
            ),
            "push_pull_legs": (
                f"Push/pull/legs split distributes volume across {days} days, "
                f"allowing high frequency and volume for {goal}. Each muscle group "
                f"is trained 2x per week with focused sessions."
            ),
            "push_pull_legs_x2": (
                f"6-day PPL split maximizes training frequency for advanced {goal}. "
                "Each muscle group is trained 2x per week with high volume per session."
            ),
        }

        return rationales.get(split_type, "Optimized training split for your goals.")

    async def suggest_exercise_swap(
        self, user_id: str, current_exercise_id: int, reason: str = "variety"
    ) -> Optional[Dict]:
        """
        Suggest an alternative exercise.
        
        Args:
            current_exercise_id: Exercise to replace
            reason: "variety", "equipment", "injury"
            
        Returns dict with suggested exercise and rationale.
        """
        # Get current exercise
        exercise_query = select(Exercise).where(Exercise.id == current_exercise_id)
        exercise_result = await self.db.execute(exercise_query)
        current_exercise = exercise_result.scalar_one_or_none()

        if not current_exercise:
            return None

        # Get substitutions
        from app.models.exercise import ExerciseSubstitution

        subs_query = (
            select(Exercise, ExerciseSubstitution.similarity, ExerciseSubstitution.reason)
            .join(
                ExerciseSubstitution,
                ExerciseSubstitution.substitute_id == Exercise.id,
            )
            .where(ExerciseSubstitution.exercise_id == current_exercise_id)
            .order_by(ExerciseSubstitution.similarity.desc())
            .limit(3)
        )
        subs_result = await self.db.execute(subs_query)
        substitutions = list(subs_result.all())

        if not substitutions:
            return None

        # Pick best substitution based on reason
        best_sub = substitutions[0]  # Highest similarity

        return {
            "suggested_exercise_id": best_sub[0].id,
            "suggested_exercise_name": best_sub[0].display_name,
            "similarity": float(best_sub[1]),
            "rationale": best_sub[2] or "Similar movement pattern and muscle targeting",
            "original_exercise": current_exercise.display_name,
        }
