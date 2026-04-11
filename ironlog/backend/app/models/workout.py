import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"
    __table_args__ = (Index("ix_workout_sessions_user_started", "user_id", "started_at"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    session_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_rpe: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    bodyweight_kg: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    total_volume_kg: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    total_sets: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="WorkoutExercise.exercise_order"
    )


class UserExercise(Base):
    __tablename__ = "user_exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    base_exercise_id: Mapped[int | None] = mapped_column(ForeignKey("exercises.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    movement_pattern: Mapped[str | None] = mapped_column(String(30), nullable=True)
    equipment: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_compound: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        CheckConstraint(
            "(exercise_id IS NOT NULL)::int + (user_exercise_id IS NOT NULL)::int = 1",
            name="ck_workout_exercises_one_exercise",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[int | None] = mapped_column(ForeignKey("exercises.id"), nullable=True)
    user_exercise_id: Mapped[int | None] = mapped_column(ForeignKey("user_exercises.id"), nullable=True)
    exercise_order: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_1rm: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    total_volume_kg: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)

    session: Mapped["WorkoutSession"] = relationship(back_populates="exercises")
    sets: Mapped[list["Set"]] = relationship(
        back_populates="workout_exercise", cascade="all, delete-orphan", order_by="Set.set_order"
    )
    exercise: Mapped["Exercise | None"] = relationship(foreign_keys=[exercise_id])  # type: ignore[name-defined]


class Set(Base):
    __tablename__ = "sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workout_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("workout_exercises.id", ondelete="CASCADE"), nullable=False
    )
    set_order: Mapped[int] = mapped_column(Integer, nullable=False)
    set_type: Mapped[str] = mapped_column(String(15), default="working", server_default="working")
    weight_kg: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    rpe: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    rir: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_pr: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    # volume_kg is a generated column — defined via server_default trick; Alembic will emit it correctly
    # We declare it as nullable so SQLAlchemy doesn't try to INSERT it
    volume_kg: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    estimated_1rm: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    workout_exercise: Mapped["WorkoutExercise"] = relationship(back_populates="sets")
