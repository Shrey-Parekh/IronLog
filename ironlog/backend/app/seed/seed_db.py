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
        # Check if already seeded
        result = await session.execute(select(MuscleGroup))
        if result.scalars().first():
            print("Muscle groups already seeded, skipping...")
            return

        # Load data
        data_path = Path(__file__).parent / "muscle_groups.json"
        with open(data_path) as f:
            muscle_groups_data = json.load(f)

        # Insert with ON CONFLICT DO NOTHING
        for mg_data in muscle_groups_data:
            stmt = insert(MuscleGroup).values(**mg_data).on_conflict_do_nothing(index_elements=["name"])
            await session.execute(stmt)

        await session.commit()
        print(f"Seeded {len(muscle_groups_data)} muscle groups")


async def seed_exercises():
    """Seed exercises, exercise_muscles, and exercise_substitutions tables."""
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(select(Exercise))
        if result.scalars().first():
            print("Exercises already seeded, skipping...")
            return

        # Load data
        data_path = Path(__file__).parent / "exercises.json"
        with open(data_path) as f:
            exercises_data = json.load(f)

        # Get muscle group name to ID mapping
        result = await session.execute(select(MuscleGroup))
        muscle_groups = {mg.name: mg.id for mg in result.scalars().all()}

        # Insert exercises
        exercise_name_to_id = {}
        for ex_data in exercises_data:
            # Extract nested data
            muscles = ex_data.pop("muscles", [])
            substitutions = ex_data.pop("substitutions", [])

            # Insert exercise
            stmt = insert(Exercise).values(**ex_data).on_conflict_do_nothing(index_elements=["name"])
            await session.execute(stmt)
            await session.flush()

            # Get exercise ID
            result = await session.execute(select(Exercise).where(Exercise.name == ex_data["name"]))
            exercise = result.scalar_one()
            exercise_name_to_id[ex_data["name"]] = exercise.id

            # Insert exercise_muscles
            for muscle_data in muscles:
                muscle_name = muscle_data["muscle"]
                if muscle_name in muscle_groups:
                    muscle_stmt = insert(ExerciseMuscle).values(
                        exercise_id=exercise.id,
                        muscle_group_id=muscle_groups[muscle_name],
                        role=muscle_data["role"],
                        activation_pct=muscle_data["activation_pct"]
                    ).on_conflict_do_nothing()
                    await session.execute(muscle_stmt)

        await session.commit()

        # Insert exercise substitutions (second pass after all exercises exist)
        for ex_data in exercises_data:
            exercise_id = exercise_name_to_id.get(ex_data["name"])
            if not exercise_id:
                continue

            # Re-parse to get substitutions
            data_path = Path(__file__).parent / "exercises.json"
            with open(data_path) as f:
                full_data = json.load(f)
            
            ex_full = next((e for e in full_data if e["name"] == ex_data["name"]), None)
            if not ex_full:
                continue

            for sub_data in ex_full.get("substitutions", []):
                substitute_name = sub_data["exercise"]
                substitute_id = exercise_name_to_id.get(substitute_name)
                if substitute_id:
                    sub_stmt = insert(ExerciseSubstitution).values(
                        exercise_id=exercise_id,
                        substitute_id=substitute_id,
                        similarity=sub_data["similarity"],
                        reason=sub_data.get("reason")
                    ).on_conflict_do_nothing()
                    await session.execute(sub_stmt)

        await session.commit()
        print(f"Seeded {len(exercises_data)} exercises with muscles and substitutions")


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
