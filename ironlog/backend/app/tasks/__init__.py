"""Celery background tasks for analytics and insights."""

from app.tasks.celery_app import celery_app

__all__ = ["celery_app"]
