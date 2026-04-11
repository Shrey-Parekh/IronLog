"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-09

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgcrypto for gen_random_uuid()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=True),
        sa.Column("body_weight_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("height_cm", sa.Numeric(5, 2), nullable=True),
        sa.Column("training_age_months", sa.Integer, nullable=False, server_default="0"),
        sa.Column("preferred_unit", sa.String(10), nullable=False, server_default="kg"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    # muscle_groups
    op.create_table(
        "muscle_groups",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("body_region", sa.String(20), nullable=False),
        sa.Column("push_pull", sa.String(10), nullable=True),
        sa.Column("default_recovery_hours", sa.Integer, nullable=False, server_default="48"),
        sa.Column("default_mrv_sets_week", sa.Integer, nullable=False, server_default="20"),
        sa.Column("default_mev_sets_week", sa.Integer, nullable=False, server_default="10"),
        sa.UniqueConstraint("name", name="uq_muscle_groups_name"),
    )

    # exercises
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(150), nullable=False),
        sa.Column("movement_pattern", sa.String(30), nullable=False),
        sa.Column("equipment", sa.String(30), nullable=False),
        sa.Column("is_compound", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_unilateral", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("supports_1rm", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("difficulty", sa.String(15), nullable=False, server_default="intermediate"),
        sa.Column("instructions", sa.Text, nullable=True),
        sa.Column("tips", sa.Text, nullable=True),
        sa.Column("common_mistakes", sa.Text, nullable=True),
        sa.UniqueConstraint("name", name="uq_exercises_name"),
    )

    # exercise_muscles
    op.create_table(
        "exercise_muscles",
        sa.Column("exercise_id", sa.Integer, sa.ForeignKey("exercises.id"), primary_key=True),
        sa.Column("muscle_group_id", sa.Integer, sa.ForeignKey("muscle_groups.id"), primary_key=True),
        sa.Column("role", sa.String(15), nullable=False),
        sa.Column("activation_pct", sa.Numeric(4, 2), nullable=False, server_default="1.0"),
    )

    # exercise_substitutions
    op.create_table(
        "exercise_substitutions",
        sa.Column("exercise_id", sa.Integer, sa.ForeignKey("exercises.id"), primary_key=True),
        sa.Column("substitute_id", sa.Integer, sa.ForeignKey("exercises.id"), primary_key=True),
        sa.Column("similarity", sa.Numeric(3, 2), nullable=False),
        sa.Column("reason", sa.String(200), nullable=True),
    )

    # user_exercises (must exist before workout_exercises FK)
    op.create_table(
        "user_exercises",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("base_exercise_id", sa.Integer, sa.ForeignKey("exercises.id"), nullable=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("movement_pattern", sa.String(30), nullable=True),
        sa.Column("equipment", sa.String(30), nullable=True),
        sa.Column("is_compound", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    # workout_sessions
    op.create_table(
        "workout_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("session_name", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("overall_rpe", sa.Numeric(3, 1), nullable=True),
        sa.Column("bodyweight_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("total_volume_kg", sa.Numeric(10, 2), nullable=True),
        sa.Column("total_sets", sa.Integer, nullable=True),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_workout_sessions_user_started", "workout_sessions", ["user_id", "started_at"])

    # workout_exercises
    op.create_table(
        "workout_exercises",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exercise_id", sa.Integer, sa.ForeignKey("exercises.id"), nullable=True),
        sa.Column("user_exercise_id", sa.Integer, sa.ForeignKey("user_exercises.id"), nullable=True),
        sa.Column("exercise_order", sa.Integer, nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("estimated_1rm", sa.Numeric(6, 2), nullable=True),
        sa.Column("total_volume_kg", sa.Numeric(8, 2), nullable=True),
        sa.CheckConstraint(
            "(exercise_id IS NOT NULL)::int + (user_exercise_id IS NOT NULL)::int = 1",
            name="ck_workout_exercises_one_exercise",
        ),
    )

    # sets — with GENERATED ALWAYS AS column
    op.create_table(
        "sets",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("workout_exercise_id", sa.Integer, sa.ForeignKey("workout_exercises.id", ondelete="CASCADE"), nullable=False),
        sa.Column("set_order", sa.Integer, nullable=False),
        sa.Column("set_type", sa.String(15), nullable=False, server_default="working"),
        sa.Column("weight_kg", sa.Numeric(6, 2), nullable=False),
        sa.Column("reps", sa.Integer, nullable=False),
        sa.Column("rpe", sa.Numeric(3, 1), nullable=True),
        sa.Column("rir", sa.Integer, nullable=True),
        sa.Column("is_pr", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("estimated_1rm", sa.Numeric(6, 2), nullable=True),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    # Add generated column separately — DDL not supported via create_table
    op.execute(
        "ALTER TABLE sets ADD COLUMN volume_kg NUMERIC(8,2) GENERATED ALWAYS AS (weight_kg * reps) STORED"
    )

    # training_programs
    op.create_table(
        "training_programs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("days_per_week", sa.Integer, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    # program_days
    op.create_table(
        "program_days",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("program_id", sa.Integer, sa.ForeignKey("training_programs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day_number", sa.Integer, nullable=False),
        sa.Column("day_name", sa.String(50), nullable=False),
        sa.Column("target_muscle_groups", postgresql.ARRAY(sa.Integer), nullable=True),
    )

    # strength_estimates
    op.create_table(
        "strength_estimates",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("exercise_id", sa.Integer, sa.ForeignKey("exercises.id"), nullable=False),
        sa.Column("estimated_at", sa.Date, nullable=False),
        sa.Column("estimated_1rm", sa.Numeric(6, 2), nullable=False),
        sa.Column("confidence_low", sa.Numeric(6, 2), nullable=True),
        sa.Column("confidence_high", sa.Numeric(6, 2), nullable=True),
        sa.Column("model_version", sa.String(20), nullable=True),
        sa.Column("data_points", sa.Integer, nullable=True),
        sa.UniqueConstraint("user_id", "exercise_id", "estimated_at", name="uq_strength_estimates"),
    )

    # muscle_group_volume
    op.create_table(
        "muscle_group_volume",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("muscle_group_id", sa.Integer, sa.ForeignKey("muscle_groups.id"), nullable=False),
        sa.Column("week_start", sa.Date, nullable=False),
        sa.Column("total_sets", sa.Integer, nullable=False),
        sa.Column("total_volume_kg", sa.Numeric(10, 2), nullable=True),
        sa.Column("avg_rpe", sa.Numeric(3, 1), nullable=True),
        sa.Column("status", sa.String(20), nullable=True),
        sa.UniqueConstraint("user_id", "muscle_group_id", "week_start", name="uq_muscle_group_volume"),
    )

    # plateau_detections
    op.create_table(
        "plateau_detections",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("exercise_id", sa.Integer, sa.ForeignKey("exercises.id"), nullable=False),
        sa.Column("detected_at", sa.Date, nullable=False),
        sa.Column("plateau_start", sa.Date, nullable=False),
        sa.Column("weeks_stalled", sa.Integer, nullable=False),
        sa.Column("estimated_1rm_at_plateau", sa.Numeric(6, 2), nullable=True),
        sa.Column("recommendation", sa.Text, nullable=True),
        sa.Column("is_resolved", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("resolved_at", sa.Date, nullable=True),
    )

    # recovery_state
    op.create_table(
        "recovery_state",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("muscle_group_id", sa.Integer, sa.ForeignKey("muscle_groups.id"), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("fatigue_score", sa.Numeric(4, 2), nullable=False),
        sa.Column("estimated_recovery_pct", sa.Numeric(4, 2), nullable=False),
        sa.Column("next_ready_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_trained_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_recovery_state_user_computed", "recovery_state", ["user_id", "computed_at"])

    # training_insights
    op.create_table(
        "training_insights",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("insight_type", sa.String(30), nullable=False),
        sa.Column("severity", sa.String(10), nullable=False, server_default="info"),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("related_exercise_id", sa.Integer, sa.ForeignKey("exercises.id"), nullable=True),
        sa.Column("related_muscle_group_id", sa.Integer, sa.ForeignKey("muscle_groups.id"), nullable=True),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_dismissed", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("ix_training_insights_user_generated", "training_insights", ["user_id", "generated_at"])


def downgrade() -> None:
    op.drop_table("training_insights")
    op.drop_table("recovery_state")
    op.drop_table("plateau_detections")
    op.drop_table("muscle_group_volume")
    op.drop_table("strength_estimates")
    op.drop_table("program_days")
    op.drop_table("training_programs")
    op.drop_table("sets")
    op.drop_table("workout_exercises")
    op.drop_table("workout_sessions")
    op.drop_table("user_exercises")
    op.drop_table("exercise_substitutions")
    op.drop_table("exercise_muscles")
    op.drop_table("exercises")
    op.drop_table("muscle_groups")
    op.drop_table("users")
