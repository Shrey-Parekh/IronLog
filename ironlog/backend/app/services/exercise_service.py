"""Exercise service."""
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.exercise import (
    Exercise,
    ExerciseMuscle,
    ExerciseSubstitution,
    MuscleGroup,
)


async def get_all_exercises(
    db: AsyncSession,
    equipment: str | None = None,
    movement_pattern: str | None = None,
    muscle_group_id: int | None = None,
    is_compound: bool | None = None,
    difficulty: str | None = None,
) -> list[Exercise]:
    """Get all exercises with optional filters."""
    query = select(Exercise).options(
        selectinload(Exercise.muscles).selectinload(ExerciseMuscle.muscle_group)
    )

    if equipment:
        query = query.where(Exercise.equipment == equipment)
    if movement_pattern:
        query = query.where(Exercise.movement_pattern == movement_pattern)
    if is_compound is not None:
        query = query.where(Exercise.is_compound == is_compound)
    if difficulty:
        query = query.where(Exercise.difficulty == difficulty)
    if muscle_group_id:
        query = query.join(ExerciseMuscle).where(
            ExerciseMuscle.muscle_group_id == muscle_group_id
        )

    result = await db.execute(query)
    return list(result.scalars().unique().all())


async def get_exercise_by_id(
    db: AsyncSession, exercise_id: int
) -> Exercise | None:
    """Get exercise by ID with muscles loaded."""
    query = (
        select(Exercise)
        .where(Exercise.id == exercise_id)
        .options(
            selectinload(Exercise.muscles).selectinload(
                ExerciseMuscle.muscle_group
            )
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def search_exercises(
    db: AsyncSession, query_str: str
) -> list[Exercise]:
    """Search exercises by name."""
    search_pattern = f"%{query_str.lower()}%"
    query = (
        select(Exercise)
        .where(
            or_(
                Exercise.name.ilike(search_pattern),
                Exercise.display_name.ilike(search_pattern),
            )
        )
        .options(
            selectinload(Exercise.muscles).selectinload(
                ExerciseMuscle.muscle_group
            )
        )
    )
    result = await db.execute(query)
    return list(result.scalars().unique().all())


async def get_exercise_substitutions(
    db: AsyncSession, exercise_id: int
) -> list[tuple[Exercise, float, str | None]]:
    """Get substitutions for an exercise."""
    query = (
        select(Exercise, ExerciseSubstitution.similarity, ExerciseSubstitution.reason)
        .join(
            ExerciseSubstitution,
            ExerciseSubstitution.substitute_id == Exercise.id,
        )
        .where(ExerciseSubstitution.exercise_id == exercise_id)
        .options(
            selectinload(Exercise.muscles).selectinload(
                ExerciseMuscle.muscle_group
            )
        )
        .order_by(ExerciseSubstitution.similarity.desc())
    )
    result = await db.execute(query)
    return list(result.all())



async def get_all_muscle_groups(db: AsyncSession) -> list[MuscleGroup]:
    """Get all muscle groups."""
    result = await db.execute(select(MuscleGroup))
    return list(result.scalars().all())


async def get_exercises_by_muscle_group(
    db: AsyncSession, muscle_group_id: int
) -> list[Exercise]:
    """Get exercises that target a specific muscle group."""
    query = (
        select(Exercise)
        .join(ExerciseMuscle)
        .where(ExerciseMuscle.muscle_group_id == muscle_group_id)
        .options(
            selectinload(Exercise.muscles).selectinload(
                ExerciseMuscle.muscle_group
            )
        )
    )
    result = await db.execute(query)
    return list(result.scalars().unique().all())
