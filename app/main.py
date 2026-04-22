import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import close_db, connect_db
from app.routers import router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

# Startup / shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_db()
    yield
    close_db()


app = FastAPI(
    title="HTTP Metadata Inventory Service",
    description="Collect and retrieve HTTP headers, cookies, and page source for any URL.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)

