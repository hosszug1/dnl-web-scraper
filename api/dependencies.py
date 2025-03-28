import os

from clients.mongo import MongoDB
from constants import (
    MONGO_DB_ENV_VAR,
    MONGO_DEFAULT_DB,
    MONGO_DEFAULT_MAX_CONNECTIONS_COUNT,
    MONGO_DEFAULT_MIN_CONNECTIONS_COUNT,
    MONGO_DEFAULT_URI,
    MONGO_MAX_CONNECTIONS_COUNT_ENV_VAR,
    MONGO_MIN_CONNECTIONS_COUNT_ENV_VAR,
    MONGO_URI_ENV_VAR,
)
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient


class CommonSettings:
    mongo_uri = os.getenv(MONGO_URI_ENV_VAR, MONGO_DEFAULT_URI)
    db_name = os.getenv(MONGO_DB_ENV_VAR, MONGO_DEFAULT_DB)


settings = CommonSettings()
db = MongoDB(settings.mongo_uri, settings.db_name)


async def mongo_connect() -> None:
    logger.info(f"Connecting to Mongo @ {db.mongo_uri}")
    db.client = AsyncIOMotorClient(
        db.mongo_uri,
        minPoolSize=os.getenv(
            MONGO_MAX_CONNECTIONS_COUNT_ENV_VAR, MONGO_DEFAULT_MIN_CONNECTIONS_COUNT
        ),
        maxPoolSize=os.getenv(
            MONGO_MIN_CONNECTIONS_COUNT_ENV_VAR, MONGO_DEFAULT_MAX_CONNECTIONS_COUNT
        ),
    )


async def mongo_close() -> None:
    logger.info("Closing mongo connection...")
    db.client.close()


async def get_settings() -> CommonSettings:
    return settings


async def get_db() -> MongoDB:
    return db
