import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class EventBus:
    _handlers: dict[str, list[Callable]] = {}

    @classmethod
    def subscribe(cls, event_name: str):
        """Decorator to subscribe a handler to an event."""
        def decorator(func: Callable):
            cls._handlers.setdefault(event_name, []).append(func)
            return func
        return decorator

    @classmethod
    async def publish(cls, event_name: str, data: dict[str, Any]):
        """Publish an event to all subscribed handlers."""
        handlers = cls._handlers.get(event_name, [])
        for handler in handlers:
            try:
                await handler(data)
            except Exception:
                logger.exception("Error in event handler for '%s'", event_name)
