"""Unit tests for database operations."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.models import MetadataRecord


def test_find_metadata_by_url_found():
    """Should return the document when it exists."""
    fake_doc = {
        "url": "https://example.com",
        "headers": {"server": "nginx"},
        "cookies": {},
        "page_source": "<html></html>",
        "collected_at": datetime.now(timezone.utc),
        "status_code": 200,
    }
    mock_collection = MagicMock()
    mock_collection.find_one = MagicMock(return_value=fake_doc)

    mock_db = MagicMock()
    mock_db.metadata = mock_collection

    with patch("app.database.get_db", return_value=mock_db):
        from app.database import find_metadata_by_url

        result = find_metadata_by_url("https://example.com")

    assert result == fake_doc


def test_find_metadata_by_url_not_found():
    """Should return None when document doesn't exist."""
    mock_collection = MagicMock()
    mock_collection.find_one = MagicMock(return_value=None)

    mock_db = MagicMock()
    mock_db.metadata = mock_collection

    with patch("app.database.get_db", return_value=mock_db):
        from app.database import find_metadata_by_url

        result = find_metadata_by_url("https://missing.example.com")

    assert result is None


def test_upsert_metadata():
    """Should call update_one with upsert=True."""
    record = MetadataRecord(
        url="https://example.com",
        headers={"server": "nginx"},
        cookies={},
        page_source="<html></html>",
        collected_at=datetime.now(timezone.utc),
        status_code=200,
    )

    mock_collection = MagicMock()
    mock_collection.update_one = MagicMock()

    mock_db = MagicMock()
    mock_db.metadata = mock_collection

    with patch("app.database.get_db", return_value=mock_db):
        from app.database import upsert_metadata

        upsert_metadata(record)

    mock_collection.update_one.assert_called_once()
    call_args = mock_collection.update_one.call_args
    assert call_args[0][0] == {"url": "https://example.com"}
    assert call_args[1]["upsert"] is True
