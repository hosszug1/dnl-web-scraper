from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dependencies import mongo_close, mongo_connect
from fastapi import FastAPI
from fastapi_pagination import add_pagination
from routers import scrape


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    await mongo_connect()
    try:
        yield
    finally:
        await mongo_close()


app = FastAPI(title="DNL Web Scraper", docs_url="/docs", lifespan=lifespan)
app.include_router(scrape.router)
add_pagination(app)
