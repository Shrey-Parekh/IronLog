"""Autoregulation engine for adaptive training recommendations."""
from datetime import date
from typing import Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.recovery_model import BanisterRecoveryModel
from app.ml.strength_curve import StrengthCurveModel


class AutoregulationEngine:
    """Provides adaptive training recommendations based on readiness and strength."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.recovery_model = BanisterRecoveryModel(db)
        self.strength_model = StrengthCurveModel(db)

    async def compute_readiness(
        self, user_id: str, muscle_group_id: int
    ) -> Dict:
        """
        Compute overall readiness for training a muscle group.
        
        Returns dict with:
        - readiness_score: 0-100 (100 = fully ready)
        - recommendation: "ready", "caution", "rest"
        - suggested_volume_adjustment: -50 to +20 (percentage)
        """
        # Get recovery state
        history = await self.recovery_model.get_training_history(
            user_id, muscle_group_id, days=30
        )
        recovery_state = self.recovery_model.compute_recovery_state(
            history, date.today()
        )

        recovery_pct = recovery_state["estimated_recovery_pct"]
        fatigue_score = recovery_state["fatigue_score"]

        # Compute readiness score (0-100)
        # Weighted combination of recovery and fatigue
        readiness_score = (recovery_pct * 0.7) + ((1 - fatigue_score) * 30)

        # Determine recommendation
        if readiness_score >= 80:
            recommendation = "ready"
            volume_adjustment = min(20, int((readiness_score - 80) / 2))
        elif readiness_score >= 60:
            recommendation = "caution"
            volume_adjustment = -int((80 - readiness_score) / 2)
        else:
            recommendation = "rest"
            volume_adjustment = -50

        return {
            "readiness_score": round(readiness_score, 1),
            "recommendation": recommendation,
            "suggested_volume_adjustment": volume_adjustment,
            "recovery_pct": recovery_pct,
            "fatigue_score": fatigue_score,
        }

    async def suggest_weight(
        self,
        user_id: str,
        exercise_id: int,
        target_reps: int,
        readiness_score: Optional[float] = None,
    ) -> Optional[Dict]:
        """
        Suggest weight for a given rep target based on strength curve and readiness.
        
        Returns dict with:
        - suggested_weight: float (kg)
        - confidence: "high", "medium", "low"
        - adjustment_reason: str
        """
        # Get strength prediction
        historical_data = await self.strength_model.get_historical_data(
            user_id, exercise_id, days=90
        )

        if not self.strength_model.fit(historical_data):
            return None

        prediction = self.strength_model.predict(days_ahead=0)
        if not prediction:
            return None

        predicted_1rm, confidence_low, confidence_high = prediction

        # Calculate base weight using Epley formula
        # weight = 1RM / (1 + reps/30)
        base_weight = predicted_1rm / (1 + target_reps / 30.0)

        # Adjust based on readiness if provided
        if readiness_score is not None:
            if readiness_score < 60:
                # Low readiness: reduce weight by 10-20%
                adjustment_factor = 0.8 + (readiness_score / 600)  # 0.8-0.9
                adjustment_reason = "Reduced due to low recovery"
            elif readiness_score > 90:
                # High readiness: can push slightly harder
                adjustment_factor = 1.0 + (readiness_score - 90) / 200  # 1.0-1.05
                adjustment_reason = "Increased due to high recovery"
            else:
                adjustment_factor = 1.0
                adjustment_reason = "Standard recommendation"
        else:
            adjustment_factor = 1.0
            adjustment_reason = "Standard recommendation"

        suggested_weight = base_weight * adjustment_factor

        # Determine confidence based on prediction interval width
        interval_width = confidence_high - confidence_low
        if interval_width < 5:
            confidence = "high"
        elif interval_width < 10:
            confidence = "medium"
        else:
            confidence = "low"

        # Round to nearest 2.5kg
        suggested_weight = round(suggested_weight / 2.5) * 2.5

        return {
            "suggested_weight": round(suggested_weight, 1),
            "confidence": confidence,
            "adjustment_reason": adjustment_reason,
            "predicted_1rm": predicted_1rm,
            "readiness_score": readiness_score,
        }

    async def suggest_rpe_target(
        self, readiness_score: float, weeks_into_mesocycle: int
    ) -> Dict:
        """
        Suggest RPE target based on readiness and training phase.
        
        Returns dict with:
        - target_rpe: float (6.0-10.0)
        - rpe_range: tuple (min, max)
        - rationale: str
        """
        # Base RPE on mesocycle phase
        if weeks_into_mesocycle <= 2:
            # Accumulation phase: moderate intensity
            base_rpe = 7.0
            rpe_range = (6.5, 7.5)
            phase = "accumulation"
        elif weeks_into_mesocycle <= 4:
            # Intensification phase: higher intensity
            base_rpe = 8.0
            rpe_range = (7.5, 8.5)
            phase = "intensification"
        else:
            # Realization phase: peak intensity
            base_rpe = 9.0
            rpe_range = (8.5, 9.5)
            phase = "realization"

        # Adjust based on readiness
        if readiness_score < 60:
            # Low readiness: reduce RPE by 1-2 points
            adjustment = -1.5 + (readiness_score / 60)  # -1.5 to -0.5
            rationale = f"Reduced from {phase} phase target due to low recovery"
        elif readiness_score > 90:
            # High readiness: can push slightly harder
            adjustment = (readiness_score - 90) / 20  # 0 to 0.5
            rationale = f"Standard {phase} phase target with high recovery"
        else:
            adjustment = 0
            rationale = f"Standard {phase} phase target"

        target_rpe = max(6.0, min(10.0, base_rpe + adjustment))
        adjusted_range = (
            max(6.0, rpe_range[0] + adjustment),
            min(10.0, rpe_range[1] + adjustment),
        )

        return {
            "target_rpe": round(target_rpe, 1),
            "rpe_range": (round(adjusted_range[0], 1), round(adjusted_range[1], 1)),
            "rationale": rationale,
            "phase": phase,
        }

    async def detect_deload_need(
        self, user_id: str, weeks: int = 4
    ) -> Dict:
        """
        Detect if user needs a deload week.
        
        Returns dict with:
        - needs_deload: bool
        - severity: "low", "medium", "high"
        - reasons: list of str
        - recommendation: str
        """
        # Get recovery states for all muscle groups
        recovery_states = await self.recovery_model.get_current_recovery_states(user_id)

        if not recovery_states:
            return {
                "needs_deload": False,
                "severity": "low",
                "reasons": [],
                "recommendation": "Continue training as normal",
            }

        # Check for signs of overreaching
        reasons = []
        severity_score = 0

        # 1. Check average recovery across all muscle groups
        avg_recovery = sum(s["estimated_recovery_pct"] for s in recovery_states) / len(
            recovery_states
        )
        if avg_recovery < 60:
            reasons.append(f"Low average recovery ({avg_recovery:.0f}%)")
            severity_score += 2
        elif avg_recovery < 70:
            reasons.append(f"Below-optimal recovery ({avg_recovery:.0f}%)")
            severity_score += 1

        # 2. Check for multiple muscle groups with high fatigue
        high_fatigue_count = sum(
            1 for s in recovery_states if s["fatigue_score"] > 0.7
        )
        if high_fatigue_count >= len(recovery_states) * 0.5:
            reasons.append(f"{high_fatigue_count} muscle groups with high fatigue")
            severity_score += 2

        # 3. Check for consistently low readiness
        low_readiness_count = sum(
            1 for s in recovery_states if s["estimated_recovery_pct"] < 70
        )
        if low_readiness_count >= len(recovery_states) * 0.6:
            reasons.append(f"{low_readiness_count} muscle groups not fully recovered")
            severity_score += 1

        # Determine severity and recommendation
        if severity_score >= 4:
            severity = "high"
            needs_deload = True
            recommendation = (
                "Take a full deload week: reduce volume by 50% and intensity by 10-15%. "
                "Focus on technique and recovery."
            )
        elif severity_score >= 2:
            severity = "medium"
            needs_deload = True
            recommendation = (
                "Consider a light deload: reduce volume by 30% for 3-4 days. "
                "Maintain intensity but cut back on total sets."
            )
        else:
            severity = "low"
            needs_deload = False
            recommendation = "Continue training as normal. Monitor recovery closely."

        return {
            "needs_deload": needs_deload,
            "severity": severity,
            "reasons": reasons,
            "recommendation": recommendation,
            "avg_recovery_pct": round(avg_recovery, 1),
        }
