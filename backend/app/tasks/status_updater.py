"""
Celery task: StatusUpdater
Runs daily at midnight to update payment and policy statuses.
"""

import asyncio
import logging

from app.core.database import async_session_factory
from app.modules.policies.status_updater import run_status_updater
from app.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.run_status_updater", bind=True, max_retries=3)
def task_run_status_updater(self) -> dict:
    """Celery task wrapper for the async StatusUpdater."""
    try:
        result = asyncio.run(_run())
        logger.info(
            "StatusUpdater completado: %d pagos, %d polizas actualizadas",
            result["payments_updated"],
            result["policies_updated"],
        )
        return result
    except Exception as exc:
        logger.error("StatusUpdater fallo: %s", exc, exc_info=True)
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


async def _run() -> dict:
    """Execute the status updater within an async session."""
    async with async_session_factory() as session:
        try:
            result = await run_status_updater(session)
            await session.commit()
            return result
        except Exception:
            await session.rollback()
            raise
