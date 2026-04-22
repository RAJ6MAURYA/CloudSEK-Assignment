"""Shared pytest fixtures."""

import asyncio
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def client():
    """Synchronous test client (useful for simple request tests)."""
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
