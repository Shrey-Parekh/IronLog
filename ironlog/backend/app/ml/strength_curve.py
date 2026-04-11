"""Strength curve modeling using Gaussian Process regression."""
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import StrengthEstimate
from app.models.workout import Set, WorkoutExercise, WorkoutSession


class StrengthCurveModel:
    """Models strength progression using Gaussian Process regression."""

    MIN_DATA_POINTS = 5  # Minimum sets needed to fit model

    def __init__(self, db: AsyncSession):
        self.db = db
        self.model: Optional[GaussianProcessRegressor] = None
        self.training_data: Optional[Tuple[np.ndarray, np.ndarray]] = None

    async def get_historical_data(
        self, user_id: str, exercise_id: int, days: int = 90
    ) -> List[Dict]:
        """
        Get historical set data for an exercise.
        
        Returns list of dicts with date, weight_kg, reps, estimated_1rm.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = (
            select(Set, WorkoutSession.started_at)
            .join(WorkoutExercise, Set.workout_exercise_id == WorkoutExercise.id)
            .join(WorkoutSession, WorkoutExercise.session_id == WorkoutSession.id)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutExercise.exercise_id == exercise_id,
                WorkoutSession.started_at >= cutoff_date,
                WorkoutSession.finished_at.isnot(None),
                Set.set_type == "working",  # Only working sets
            )
            .order_by(WorkoutSession.started_at)
        )
        result = await self.db.execute(query)
        rows = list(result.all())

        data = []
        for set_obj, started_at in rows:
            if set_obj.estimated_1rm:
                data.append({
                    "date": started_at.date(),
                    "weight_kg": float(set_obj.weight_kg),
                    "reps": set_obj.reps,
                    "estimated_1rm": float(set_obj.estimated_1rm),
                })

        return data

    def fit(self, historical_data: List[Dict]) -> bool:
        """
        Fit Gaussian Process model to historical data.
        
        Returns True if successful, False if insufficient data.
        """
        if len(historical_data) < self.MIN_DATA_POINTS:
            return False

        # Convert dates to days since first session
        dates = [d["date"] for d in historical_data]
        first_date = min(dates)
        X = np.array([(d - first_date).days for d in dates]).reshape(-1, 1)
        y = np.array([d["estimated_1rm"] for d in historical_data])

        # Store for later use
        self.training_data = (X, y, first_date)

        # Matern kernel with noise
        kernel = Matern(length_scale=14.0, nu=2.5) + WhiteKernel(noise_level=1.0)
        self.model = GaussianProcessRegressor(
            kernel=kernel,
            n_restarts_optimizer=10,
            alpha=1e-6,
            normalize_y=True,
        )

        self.model.fit(X, y)
        return True

    def predict(
        self, days_ahead: int = 0
    ) -> Optional[Tuple[float, float, float]]:
        """
        Predict 1RM with confidence interval.
        
        Args:
            days_ahead: Days into the future to predict (0 = today)
            
        Returns:
            (predicted_1rm, confidence_low, confidence_high) or None if model not fitted
        """
        if self.model is None or self.training_data is None:
            return None

        X_train, _, first_date = self.training_data
        target_date = date.today() + timedelta(days=days_ahead)
        days_since_first = (target_date - first_date).days

        X_pred = np.array([[days_since_first]])
        y_pred, y_std = self.model.predict(X_pred, return_std=True)

        predicted_1rm = float(y_pred[0])
        # 95% confidence interval (±1.96 std)
        confidence_low = float(predicted_1rm - 1.96 * y_std[0])
        confidence_high = float(predicted_1rm + 1.96 * y_std[0])

        return (
            round(predicted_1rm, 2),
            round(max(0, confidence_low), 2),
            round(confidence_high, 2),
        )

    def predict_reps_at_weight(self, target_weight: float) -> Optional[int]:
        """
        Predict how many reps can be performed at a given weight.
        
        Uses reverse Epley formula: reps = 30 * (1RM / weight - 1)
        """
        prediction = self.predict(days_ahead=0)
        if not prediction:
            return None

        predicted_1rm, _, _ = prediction

        if target_weight >= predicted_1rm:
            return 1

        # Reverse Epley formula
        reps = 30 * (predicted_1rm / target_weight - 1)
        return max(1, int(round(reps)))

    async def get_strength_timeline(
        self, user_id: str, exercise_id: int, days: int = 90
    ) -> List[Dict]:
        """
        Get strength progression timeline with predictions.
        
        Returns list of dicts with date, actual_1rm (if available), predicted_1rm, confidence_low, confidence_high.
        """
        historical_data = await self.get_historical_data(user_id, exercise_id, days)

        if not self.fit(historical_data):
            # Not enough data, return raw data only
            return [
                {
                    "date": d["date"],
                    "actual_1rm": d["estimated_1rm"],
                    "predicted_1rm": None,
                    "confidence_low": None,
                    "confidence_high": None,
                }
                for d in historical_data
            ]

        # Generate timeline with predictions
        if not self.training_data:
            return []

        _, _, first_date = self.training_data
        timeline = []

        # Create a dict of actual values by date
        actual_by_date = {}
        for d in historical_data:
            date_key = d["date"]
            if date_key not in actual_by_date:
                actual_by_date[date_key] = []
            actual_by_date[date_key].append(d["estimated_1rm"])

        # Average multiple sets on same day
        actual_by_date = {
            k: sum(v) / len(v) for k, v in actual_by_date.items()
        }

        # Generate predictions for each day
        start_date = min(historical_data, key=lambda x: x["date"])["date"]
        end_date = date.today()
        current_date = start_date

        while current_date <= end_date:
            days_since_first = (current_date - first_date).days
            X_pred = np.array([[days_since_first]])
            y_pred, y_std = self.model.predict(X_pred, return_std=True)

            timeline.append({
                "date": current_date,
                "actual_1rm": actual_by_date.get(current_date),
                "predicted_1rm": round(float(y_pred[0]), 2),
                "confidence_low": round(max(0, float(y_pred[0] - 1.96 * y_std[0])), 2),
                "confidence_high": round(float(y_pred[0] + 1.96 * y_std[0]), 2),
            })

            current_date += timedelta(days=1)

        return timeline

    async def save_estimate(
        self, user_id: str, exercise_id: int, estimated_at: date
    ) -> None:
        """Save current strength estimate to database."""
        prediction = self.predict(days_ahead=0)
        if not prediction:
            return

        predicted_1rm, confidence_low, confidence_high = prediction

        estimate = StrengthEstimate(
            user_id=user_id,
            exercise_id=exercise_id,
            estimated_at=estimated_at,
            estimated_1rm=predicted_1rm,
            confidence_low=confidence_low,
            confidence_high=confidence_high,
            model_version="gp_matern_v1",
            data_points=len(self.training_data[0]) if self.training_data else 0,
        )

        self.db.add(estimate)
        await self.db.commit()
