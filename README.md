# HTTP Metadata Inventory Service

A FastAPI service that collects and retrieves HTTP metadata (headers, cookies, page source) for any given URL, backed by MongoDB.

## Architecture

```
app/
├── main.py        # FastAPI app factory & lifespan
├── config.py      # Settings via environment variables
├── models.py      # Pydantic request/response models
├── routes.py      # API endpoints (POST & GET /metadata/)
├── service.py     # HTTP metadata collection logic
└── database.py    # MongoDB connection & data access layer
tests/
├── conftest.py        # Shared fixtures
├── test_service.py    # Unit tests for collection logic
├── test_database.py   # Unit tests for DB operations
└── test_routes.py     # Integration tests for API endpoints
```

## Quick Start

### Prerequisites
- Docker & Docker Compose

### Run

```bash
docker-compose up --build
```

### Stop

```bash
docker-compose down
```

## API Endpoints

### `POST /metadata/`
Collect and store metadata for a URL.

**Request body:**
```json
{ "url": "https://example.com" }

Make sure the request has 
``` json
Content-Type: application/json header.
```
```

**Response (201):**
```json
{
  "message": "Metadata collected and stored successfully.",
  "url": "https://example.com",
  "status_code": 200,
  "collected_at": "2025-01-01T00:00:00Z"
}
```

### `GET /metadata/?url=https://example.com`
Retrieve stored metadata for a URL.

- **200** — Record found; returns full headers, cookies, and page source.
- **202** — Record not found; background collection has been triggered. Retry shortly.

## Background Worker Logic

When a `GET` request encounters a cache miss, the service:
1. Responds immediately with `202 Accepted`.
2. Spawns an internal `asyncio.create_task()` to fetch and store the metadata.
4. Subsequent `GET` requests for the same URL will return the full data once collection finishes.

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MONGO_URI` | `mongodb://mongodb:27017` | MongoDB connection string |
| `MONGO_DB_NAME` | `http_metadata` | Database name |
| `REQUEST_TIMEOUT` | `30` | HTTP request timeout (seconds) |
