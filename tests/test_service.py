"""Unit tests for the metadata collection service layer."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import requests
import pytest

from app.models import MetadataRecord
from app.service import collect_metadata


def test_collect_metadata_success():
    """collect_metadata should return a MetadataRecord on success."""
    mock_response = MagicMock()
    mock_response.headers = {"content-type": "text/html", "server": "nginx"}
    mock_response.cookies = requests.cookies.RequestsCookieJar()
    mock_response.cookies.set("session_id", "abc123")
    mock_response.text = "<html><body>Hello</body></html>"
    mock_response.status_code = 200

    with patch("app.service.requests.get", return_value=mock_response):
        record = collect_metadata("https://example.com")

    assert isinstance(record, MetadataRecord)
    assert record.url == "https://example.com"
    assert record.headers["content-type"] == "text/html"
    assert record.cookies["session_id"] == "abc123"
    assert "Hello" in record.page_source
    assert record.status_code == 200

# collect_metadata should propagate timeout errors
def test_collect_metadata_timeout():
    with patch(
        "app.service.requests.get",
        side_effect=requests.exceptions.ReadTimeout("timed out"),
    ):
        with pytest.raises(requests.exceptions.ReadTimeout):
            collect_metadata("https://slow-site.example.com")
