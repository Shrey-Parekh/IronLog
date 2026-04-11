"""API router aggregator."""
from fastapi import APIRouter

from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.exercises import router as exercises_router
from app.api.programs import router as programs_router
from app.api.recommendations import router as recommendations_router
from app.api.workouts import router as workouts_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(exercises_router, tags=["exercises"])
api_router.include_router(workouts_router, prefix="/workouts", tags=["workouts"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(programs_router, tags=["programs"])
api_router.include_router(recommendations_router, tags=["recommendations"])
