"""Celery application factory."""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "protegrt",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.status_updater"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Import beat schedule configuration
from app.tasks.scheduler import beat_schedule  # noqa: E402

celery_app.conf.beat_schedule = beat_schedule
celery_app.conf.timezone = "America/Mexico_City"
