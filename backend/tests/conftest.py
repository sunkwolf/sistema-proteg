"""Root conftest — shared fixtures for all tests."""

import asyncio
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.core.database import get_db
from app.core.redis import get_redis
from app.main import create_app
from app.models.enums import PaymentStatusType, PolicyStatusType


# ── Event loop ────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Mock DB session ───────────────────────────────────────────────────


@pytest.fixture
def mock_db():
    """AsyncSession mock for unit tests."""
    session = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    return session


# ── Mock Redis ────────────────────────────────────────────────────────


@pytest.fixture
def mock_redis():
    """Redis mock for auth tests."""
    r = AsyncMock()
    r.exists = AsyncMock(return_value=False)
    r.get = AsyncMock(return_value=None)
    r.setex = AsyncMock()
    r.delete = AsyncMock()
    r.incr = AsyncMock(return_value=1)
    r.expire = AsyncMock()
    r.scan_iter = AsyncMock(return_value=iter([]))
    return r


# ── App + HTTP client ────────────────────────────────────────────────


@pytest.fixture
def app(mock_db, mock_redis):
    """FastAPI app with dependency overrides for testing."""
    application = create_app()

    async def override_get_db():
        yield mock_db

    async def override_get_redis():
        return mock_redis

    application.dependency_overrides[get_db] = override_get_db
    application.dependency_overrides[get_redis] = override_get_redis

    yield application

    application.dependency_overrides.clear()


@pytest.fixture
async def client(app):
    """Async HTTP client for integration tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ── Model factories (lightweight, no factory_boy needed) ──────────────


def make_payment(
    *,
    id: int = 1,
    policy_id: int = 1,
    payment_number: int = 1,
    amount: Decimal = Decimal("1000.00"),
    due_date: date | None = None,
    status: PaymentStatusType = PaymentStatusType.PENDING,
    seller_id: int | None = None,
    collector_id: int | None = None,
    actual_date: date | None = None,
    **kwargs,
) -> MagicMock:
    """Create a mock Payment object."""
    p = MagicMock()
    p.id = id
    p.policy_id = policy_id
    p.payment_number = payment_number
    p.amount = amount
    p.due_date = due_date or date.today()
    p.status = status
    p.seller_id = seller_id
    p.collector_id = collector_id
    p.actual_date = actual_date
    for k, v in kwargs.items():
        setattr(p, k, v)
    return p


def make_policy(
    *,
    id: int = 1,
    folio: int = 10001,
    status: PolicyStatusType = PolicyStatusType.PENDING,
    effective_date: date | None = None,
    expiration_date: date | None = None,
    **kwargs,
) -> MagicMock:
    """Create a mock Policy object."""
    p = MagicMock()
    p.id = id
    p.folio = folio
    p.status = status
    p.effective_date = effective_date or date.today()
    p.expiration_date = expiration_date or (date.today() + timedelta(days=365))
    for k, v in kwargs.items():
        setattr(p, k, v)
    return p
