"""
Celery Beat scheduler configuration.
Defines periodic tasks (status updater, report generation, etc.)
"""

from celery.schedules import crontab

beat_schedule = {
    "status-updater-midnight": {
        "task": "tasks.run_status_updater",
        "schedule": crontab(hour=0, minute=0),
        "options": {"queue": "default"},
    },
}
