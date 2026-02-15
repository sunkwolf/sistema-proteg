import pytest


@pytest.fixture
def anyio_backend():
    return "asyncio"


# Database and HTTP client fixtures will be added in Fase 1
