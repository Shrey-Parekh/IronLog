"""Analytics models for strength estimates, volume tracking, and insights."""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class StrengthEstimate(Base):
    """Stores estimated 1RM values over time for tracking strength progression."""

    __tablename__ = "strength_estimates"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "exercise_id", "estimated_at", name="uq_strength_estimates"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id"), nullable=False
    )
    estimated_at: Mapped[date] = mapped_column(Date, nullable=False)
    estimated_1rm: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    confidence_low: Mapped[float | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    confidence_high: Mapped[float | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    model_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    data_points: Mapped[int | None] = mapped_column(Integer, nullable=True)


class MuscleGroupVolume(Base):
    """Tracks weekly training volume per muscle group."""

    __tablename__ = "muscle_group_volume"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "muscle_group_id", "week_start", name="uq_muscle_group_volume"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    muscle_group_id: Mapped[int] = mapped_column(
        ForeignKey("muscle_groups.id"), nullable=False
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    total_sets: Mapped[int] = mapped_column(Integer, nullable=False)
    total_volume_kg: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    avg_rpe: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)


class PlateauDetection(Base):
    """Records detected training plateaus and recommendations."""

    __tablename__ = "plateau_detections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id"), nullable=False
    )
    detected_at: Mapped[date] = mapped_column(Date, nullable=False)
    plateau_start: Mapped[date] = mapped_column(Date, nullable=False)
    weeks_stalled: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_1rm_at_plateau: Mapped[float | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    resolved_at: Mapped[date | None] = mapped_column(Date, nullable=True)


class RecoveryState(Base):
    """Tracks muscle group recovery and fatigue state."""

    __tablename__ = "recovery_state"
    __table_args__ = (
        Index("ix_recovery_state_user_computed", "user_id", "computed_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    muscle_group_id: Mapped[int] = mapped_column(
        ForeignKey("muscle_groups.id"), nullable=False
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"), nullable=False
    )
    fatigue_score: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    estimated_recovery_pct: Mapped[float] = mapped_column(
        Numeric(4, 2), nullable=False
    )
    next_ready_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_trained_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class TrainingInsight(Base):
    """Stores AI-generated training insights and recommendations."""

    __tablename__ = "training_insights"
    __table_args__ = (
        Index("ix_training_insights_user_generated", "user_id", "generated_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"), nullable=False
    )
    insight_type: Mapped[str] = mapped_column(String(30), nullable=False)
    severity: Mapped[str] = mapped_column(
        String(10), default="info", server_default="info"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    related_exercise_id: Mapped[int | None] = mapped_column(
        ForeignKey("exercises.id"), nullable=True
    )
    related_muscle_group_id: Mapped[int | None] = mapped_column(
        ForeignKey("muscle_groups.id"), nullable=True
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    is_dismissed: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
