"""Integration tests for API endpoints."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.models import MetadataRecord


@pytest.fixture(autouse=True)
def _mock_db_lifecycle():
    """Prevent real MongoDB connections during tests."""
    with (
        patch("app.main.connect_db"),
        patch("app.main.close_db"),
    ):
        yield


@pytest.fixture()
def _sample_record():
    return {
        "url": "https://example.com/",
        "headers": {"content-type": "text/html"},
        "cookies": {"session": "xyz"},
        "page_source": "<html>test</html>",
        "collected_at": datetime(2025, 1, 1, tzinfo=timezone.utc),
        "status_code": 200,
    }


class TestPostEndpoint:
    """Tests for POST /metadata/."""

    def test_post_success(self, client):
        """POST should collect metadata and return 201."""
        fake_record = MetadataRecord(
            url="https://example.com/",
            headers={"content-type": "text/html"},
            cookies={},
            page_source="<html></html>",
            collected_at=datetime.now(timezone.utc),
            status_code=200,
        )
        with (
            patch(
                "app.routes.collect_metadata",
                return_value=fake_record,
            ),
            patch("app.routes.upsert_metadata"),
        ):
            resp = client.post("/metadata/", json={"url": "https://example.com"})

        assert resp.status_code == 201
        data = resp.json()
        assert data["url"] == "https://example.com/"
        assert data["status_code"] == 200

    def test_post_invalid_url(self, client):
        """POST with invalid URL should return 422."""
        resp = client.post("/metadata/", json={"url": "not-a-url"})
        assert resp.status_code == 422

    def test_post_fetch_failure(self, client):
        """POST should return 502 when the target URL is unreachable."""
        with patch(
            "app.routes.collect_metadata",
            side_effect=Exception("Connection refused"),
        ):
            resp = client.post(
                "/metadata/", json={"url": "https://unreachable.example.com"}
            )

        assert resp.status_code == 502
        assert "Failed to fetch URL" in resp.json()["detail"]


class TestGetEndpoint:
    """Tests for GET /metadata/."""

    def test_get_existing_record(self, client, _sample_record):
        """GET should return 200 with full metadata when record exists."""
        with patch(
            "app.routes.find_metadata_by_url",
            return_value=_sample_record,
        ):
            resp = client.get(
                "/metadata/", params={"url": "https://example.com"}
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["url"] == "https://example.com/"
        assert "headers" in data
        assert "cookies" in data
        assert "page_source" in data

    def test_get_missing_record_returns_202(self, client):
        """GET should return 202 and trigger background collection on cache miss."""
        with (
            patch(
                "app.routes.find_metadata_by_url",
                return_value=None,
            ),
            patch("asyncio.create_task") as mock_task,
        ):
            resp = client.get(
                "/metadata/", params={"url": "https://new-site.example.com"}
            )

        assert resp.status_code == 202
        data = resp.json()
        assert "accepted" in data["message"].lower() or "queued" in data["message"].lower()
        mock_task.assert_called_once()

    def test_get_invalid_url(self, client):
        """GET with missing url param should return 422."""
        resp = client.get("/metadata/")
        assert resp.status_code == 422
