"""Plateau detection using PELT changepoint analysis."""
from datetime import date, timedelta
from typing import Dict, List, Optional

import numpy as np
import ruptures as rpt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import PlateauDetection, StrengthEstimate


class PlateauDetector:
    """Detects training plateaus using changepoint detection."""

    MIN_DATA_POINTS = 10  # Minimum data points for PELT
    PLATEAU_THRESHOLD_WEEKS = 3  # Weeks of stagnation to consider plateau

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_strength_history(
        self, user_id: str, exercise_id: int, days: int = 180
    ) -> List[Dict]:
        """Get historical strength estimates."""
        cutoff_date = date.today() - timedelta(days=days)

        query = (
            select(StrengthEstimate)
            .where(
                StrengthEstimate.user_id == user_id,
                StrengthEstimate.exercise_id == exercise_id,
                StrengthEstimate.estimated_at >= cutoff_date,
            )
            .order_by(StrengthEstimate.estimated_at)
        )
        result = await self.db.execute(query)
        estimates = list(result.scalars().all())

        return [
            {
                "date": est.estimated_at,
                "estimated_1rm": float(est.estimated_1rm),
            }
            for est in estimates
        ]

    def detect(self, strength_history: List[Dict]) -> Optional[Dict]:
        """
        Detect plateau using PELT changepoint detection.
        
        Returns dict with plateau info or None if no plateau detected:
        - plateau_start: date
        - plateau_end: date (today)
        - weeks_stalled: int
        - estimated_1rm_at_plateau: float
        - changepoint_score: float
        """
        if len(strength_history) < self.MIN_DATA_POINTS:
            return None

        # Extract 1RM values
        dates = [d["date"] for d in strength_history]
        values = np.array([d["estimated_1rm"] for d in strength_history])

        # PELT changepoint detection
        model = "l2"  # L2 norm for mean shift detection
        algo = rpt.Pelt(model=model, min_size=3, jump=1)
        algo.fit(values)

        # Detect changepoints with penalty
        penalty = 3.0  # Higher = fewer changepoints
        try:
            changepoints = algo.predict(pen=penalty)
        except Exception:
            return None

        if not changepoints or len(changepoints) < 2:
            return None

        # Get the last segment (most recent)
        last_changepoint_idx = changepoints[-2]  # -1 is the end
        last_segment = values[last_changepoint_idx:]
        last_segment_dates = dates[last_changepoint_idx:]

        # Check if last segment shows stagnation
        if len(last_segment) < 3:
            return None

        # Calculate trend in last segment
        x = np.arange(len(last_segment))
        slope, _ = np.polyfit(x, last_segment, 1)

        # Plateau if slope is near zero or negative
        # Threshold: less than 0.5kg improvement per data point
        if slope > 0.5:
            return None

        # Calculate duration
        plateau_start = last_segment_dates[0]
        plateau_end = dates[-1]
        weeks_stalled = (plateau_end - plateau_start).days / 7

        if weeks_stalled < self.PLATEAU_THRESHOLD_WEEKS:
            return None

        return {
            "plateau_start": plateau_start,
            "plateau_end": plateau_end,
            "weeks_stalled": int(weeks_stalled),
            "estimated_1rm_at_plateau": round(float(np.mean(last_segment)), 2),
            "changepoint_score": abs(float(slope)),
        }

    def generate_recommendation(self, plateau_info: Dict, exercise_name: str) -> str:
        """Generate contextual recommendation for breaking plateau."""
        weeks = plateau_info["weeks_stalled"]

        if weeks < 4:
            return (
                f"Your {exercise_name} has stalled for {weeks} weeks. "
                "Try increasing volume by 10-20% or adding a variation exercise."
            )
        elif weeks < 8:
            return (
                f"Your {exercise_name} has plateaued for {weeks} weeks. "
                "Consider a deload week (50% volume) followed by a new rep range "
                "(e.g., switch from 8-12 reps to 4-6 reps for 3-4 weeks)."
            )
        else:
            return (
                f"Your {exercise_name} has been stuck for {weeks} weeks. "
                "Time for a significant change: take a full deload week, then switch "
                "to a different exercise variation or movement pattern for 4-6 weeks "
                "before returning to this lift."
            )

    async def check_resolved(
        self, user_id: str, exercise_id: int, plateau_start: date
    ) -> bool:
        """Check if a previously detected plateau has been resolved."""
        # Get recent estimates since plateau
        query = (
            select(StrengthEstimate)
            .where(
                StrengthEstimate.user_id == user_id,
                StrengthEstimate.exercise_id == exercise_id,
                StrengthEstimate.estimated_at >= plateau_start,
            )
            .order_by(StrengthEstimate.estimated_at)
        )
        result = await self.db.execute(query)
        estimates = list(result.scalars().all())

        if len(estimates) < 5:
            return False

        # Check for upward trend
        values = [float(e.estimated_1rm) for e in estimates[-5:]]
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)

        # Resolved if showing consistent improvement (>1kg per data point)
        return slope > 1.0

    async def save_detection(
        self,
        user_id: str,
        exercise_id: int,
        plateau_info: Dict,
        recommendation: str,
    ) -> None:
        """Save plateau detection to database."""
        detection = PlateauDetection(
            user_id=user_id,
            exercise_id=exercise_id,
            detected_at=date.today(),
            plateau_start=plateau_info["plateau_start"],
            weeks_stalled=plateau_info["weeks_stalled"],
            estimated_1rm_at_plateau=plateau_info["estimated_1rm_at_plateau"],
            recommendation=recommendation,
            is_resolved=False,
        )

        self.db.add(detection)
        await self.db.commit()

    async def get_active_plateaus(self, user_id: str) -> List[PlateauDetection]:
        """Get all active (unresolved) plateaus for a user."""
        query = select(PlateauDetection).where(
            PlateauDetection.user_id == user_id,
            PlateauDetection.is_resolved == False,
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
