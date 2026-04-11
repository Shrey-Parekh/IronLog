"""Celery application configuration."""
from celery import Celery
from app.config import settings

celery_app = Celery(
    "ironlog",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.post_session",
        "app.tasks.nightly",
        "app.tasks.weekly",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "nightly-analytics": {
        "task": "app.tasks.nightly.run_nightly_analytics",
        "schedule": 3600 * 24,  # Daily at 2 AM UTC
        "options": {"expires": 3600},
    },
    "weekly-summary": {
        "task": "app.tasks.weekly.run_weekly_summary",
        "schedule": 3600 * 24 * 7,  # Weekly on Sunday 8 PM UTC
        "options": {"expires": 3600},
    },
}
