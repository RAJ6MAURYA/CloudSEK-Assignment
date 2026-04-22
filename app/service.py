import logging
from datetime import datetime, timezone

import requests

from app.config import settings
from app.models import MetadataRecord

logger = logging.getLogger(__name__)


def collect_metadata(url: str) -> MetadataRecord:
    """
    Fetch the given URL and extract headers, cookies, and page source.

    Raises requests.RequestException on network/timeout failures.
    """
    response = requests.get(
        url,
        timeout=settings.request_timeout,
        allow_redirects=True,
    )

    headers = dict(response.headers)
    cookies = {k: v for k, v in response.cookies.items()}
    page_source = response.text

    return MetadataRecord(
        url=url,
        headers=headers,
        cookies=cookies,
        page_source=page_source,
        collected_at=datetime.now(timezone.utc),
        status_code=response.status_code,
    )
