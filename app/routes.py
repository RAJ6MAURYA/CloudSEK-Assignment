
import asyncio
import logging

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import HttpUrl

from app.database import find_metadata_by_url, upsert_metadata, delete_metadata
from app.models import (
    AcceptedResponse,
    ErrorResponse,
    MetadataResponse,
    PostSuccessResponse,
    URLRequest,
)
from app.service import collect_metadata

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metadata", tags=["Metadata"])

# Background task: collect metadata and persist it.
async def _background_collect(url: str) -> None:
    try:
        record = await asyncio.to_thread(collect_metadata, url)
        await asyncio.to_thread(upsert_metadata, record)
        logger.info("Background collection completed for %s", url)
    except Exception:
        logger.exception("Background collection failed for %s", url)


# Collect headers, cookies, and page source for the given URL
# and store the result in MongoDB.
@router.post(
    "/",
    response_model=PostSuccessResponse,
    status_code=201,
    responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
    summary="Collect and store metadata for a URL",
)
async def create_metadata(body: URLRequest):
    url = str(body.url)
    try:
        record = await asyncio.to_thread(collect_metadata, url)
    except Exception as exc:
        logger.exception("Failed to collect metadata for %s", url)
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch URL: {exc}",
        )

    await asyncio.to_thread(upsert_metadata, record)

    return PostSuccessResponse(
        url=record.url,
        status_code=record.status_code,
        collected_at=record.collected_at,
    )


# Return cached metadata if available.
# Otherwise respond with 202 and trigger background collection.
@router.get(
    "/",
    response_model=MetadataResponse,
    responses={
        202: {"model": AcceptedResponse},
        400: {"model": ErrorResponse},
    },
    summary="Retrieve metadata for a URL",
)
async def get_metadata(url: HttpUrl = Query(..., description="The URL to look up")):
    url_str = str(url)
    existing = await asyncio.to_thread(find_metadata_by_url, url_str)

    if existing:
        return MetadataResponse(**existing)

    # Cache miss – schedule async background collection
    asyncio.create_task(_background_collect(url_str))

    return JSONResponse(
        status_code=202,
        content=AcceptedResponse(url=url_str).model_dump(),
    )

@router.delete("/del")
async def delete_metadata_route(body: URLRequest):
    url = str(body.url)
    print(url,type(url))
    await asyncio.to_thread(delete_metadata,url)

    return JSONResponse(
        status_code=202,
        content=AcceptedResponse(url=url).model_dump(),
    )