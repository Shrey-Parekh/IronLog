from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MuscleGroup(Base):
    __tablename__ = "muscle_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    body_region: Mapped[str] = mapped_column(String(20), nullable=False)
    push_pull: Mapped[str | None] = mapped_column(String(10), nullable=True)
    default_recovery_hours: Mapped[int] = mapped_column(Integer, default=48, server_default="48")
    default_mrv_sets_week: Mapped[int] = mapped_column(Integer, default=20, server_default="20")
    default_mev_sets_week: Mapped[int] = mapped_column(Integer, default=10, server_default="10")

    exercise_muscles: Mapped[list["ExerciseMuscle"]] = relationship(back_populates="muscle_group")


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    movement_pattern: Mapped[str] = mapped_column(String(30), nullable=False)
    equipment: Mapped[str] = mapped_column(String(30), nullable=False)
    is_compound: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    is_unilateral: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    supports_1rm: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    difficulty: Mapped[str] = mapped_column(String(15), default="intermediate", server_default="intermediate")
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    tips: Mapped[str | None] = mapped_column(Text, nullable=True)
    common_mistakes: Mapped[str | None] = mapped_column(Text, nullable=True)

    muscles: Mapped[list["ExerciseMuscle"]] = relationship(back_populates="exercise", cascade="all, delete-orphan")
    substitutions_from: Mapped[list["ExerciseSubstitution"]] = relationship(
        foreign_keys="ExerciseSubstitution.exercise_id", back_populates="exercise", cascade="all, delete-orphan"
    )


class ExerciseMuscle(Base):
    __tablename__ = "exercise_muscles"

    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), primary_key=True)
    muscle_group_id: Mapped[int] = mapped_column(ForeignKey("muscle_groups.id"), primary_key=True)
    role: Mapped[str] = mapped_column(String(15), nullable=False)
    activation_pct: Mapped[float] = mapped_column(Numeric(4, 2), default=1.0, server_default="1.0")

    exercise: Mapped["Exercise"] = relationship(back_populates="muscles")
    muscle_group: Mapped["MuscleGroup"] = relationship(back_populates="exercise_muscles")


class ExerciseSubstitution(Base):
    __tablename__ = "exercise_substitutions"

    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), primary_key=True)
    substitute_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), primary_key=True)
    similarity: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(200), nullable=True)

    exercise: Mapped["Exercise"] = relationship(foreign_keys=[exercise_id], back_populates="substitutions_from")
    substitute: Mapped["Exercise"] = relationship(foreign_keys=[substitute_id])
