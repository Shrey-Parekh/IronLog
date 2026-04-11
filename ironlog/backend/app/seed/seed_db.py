"""Seed database with exercise knowledge base."""
import asyncio
import json
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert

from app.database import AsyncSessionLocal
from app.models.exercise import Exercise, ExerciseMuscle, ExerciseSubstitution, MuscleGroup


async def seed_muscle_groups():
    """Seed muscle groups table."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(MuscleGroup))
        if result.scalars().first():
            print("Muscle groups already seeded, skipping...")
            return

        data_path = Path(__file__).parent / "muscle_groups.json"
        with open(data_path) as f:
            muscle_groups_data = json.load(f)

        for mg_data in muscle_groups_data:
            stmt = insert(MuscleGroup).values(**mg_data).on_conflict_do_nothing(
                index_elements=["name"]
            )
            await session.execute(stmt)

        await session.commit()
        print(f"Seeded {len(muscle_groups_data)} muscle groups")


async def seed_exercises():
    """Seed exercises, exercise_muscles, and exercise_substitutions tables."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Exercise))
        if result.scalars().first():
            print("Exercises already seeded, skipping...")
            return

        # Load data once
        data_path = Path(__file__).parent / "exercises.json"
        with open(data_path) as f:
            exercises_data = json.load(f)

        # Get muscle group name → ID mapping
        result = await session.execute(select(MuscleGroup))
        muscle_groups = {mg.name: mg.id for mg in result.scalars().all()}

        if not muscle_groups:
            print("ERROR: No muscle groups found. Run seed_muscle_groups first.")
            return

        # Pass 1: Insert exercises and exercise_muscles
        exercise_name_to_id = {}
        skipped_muscles = set()

        for ex_data in exercises_data:
            muscles = ex_data.pop("muscles", [])
            ex_data.pop("substitutions", None)  # Remove, handled in pass 2

            stmt = insert(Exercise).values(**ex_data).on_conflict_do_nothing(
                index_elements=["name"]
            )
            await session.execute(stmt)
            await session.flush()

            # Get the exercise ID
            result = await session.execute(
                select(Exercise).where(Exercise.name == ex_data["name"])
            )
            exercise = result.scalar_one()
            exercise_name_to_id[ex_data["name"]] = exercise.id

            # Insert exercise_muscles
            for muscle_data in muscles:
                muscle_name = muscle_data["muscle"]
                if muscle_name not in muscle_groups:
                    skipped_muscles.add(muscle_name)
                    continue

                muscle_stmt = insert(ExerciseMuscle).values(
                    exercise_id=exercise.id,
                    muscle_group_id=muscle_groups[muscle_name],
                    role=muscle_data["role"],
                    activation_pct=muscle_data["activation_pct"],
                ).on_conflict_do_nothing()
                await session.execute(muscle_stmt)

        await session.commit()

        if skipped_muscles:
            print(f"WARNING: Skipped unknown muscle groups: {skipped_muscles}")

        # Pass 2: Insert substitutions (all exercises now exist)
        # Re-read the raw data to get substitutions
        with open(data_path) as f:
            exercises_raw = json.load(f)

        sub_count = 0
        skipped_subs = set()

        for ex_raw in exercises_raw:
            exercise_id = exercise_name_to_id.get(ex_raw["name"])
            if not exercise_id:
                continue

            for sub_data in ex_raw.get("substitutions", []):
                substitute_name = sub_data["exercise"]
                substitute_id = exercise_name_to_id.get(substitute_name)

                if not substitute_id:
                    skipped_subs.add(substitute_name)
                    continue

                sub_stmt = insert(ExerciseSubstitution).values(
                    exercise_id=exercise_id,
                    substitute_id=substitute_id,
                    similarity=sub_data["similarity"],
                    reason=sub_data.get("reason"),
                ).on_conflict_do_nothing()
                await session.execute(sub_stmt)
                sub_count += 1

        await session.commit()

        if skipped_subs:
            print(f"WARNING: Skipped substitution refs (exercise not found): {skipped_subs}")

        print(
            f"Seeded {len(exercises_data)} exercises, "
            f"{sub_count} substitutions"
        )


async def main():
    """Run all seed functions."""
    print("Starting database seed...")

    # Enable pgcrypto extension for gen_random_uuid()
    async with AsyncSessionLocal() as session:
        await session.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        await session.commit()

    await seed_muscle_groups()
    await seed_exercises()

    print("Database seed complete!")


if __name__ == "__main__":
    asyncio.run(main())
