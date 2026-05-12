from collections.abc import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


class MongoClientManager:
    def __init__(self) -> None:
        self._client: AsyncIOMotorClient | None = None

    def connect(self) -> None:
        if self._client is None:
            settings = get_settings()
            self._client = AsyncIOMotorClient(settings.mongo_uri)

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    @property
    def database(self) -> AsyncIOMotorDatabase:
        if self._client is None:
            raise RuntimeError("MongoDB client is not connected")
        settings = get_settings()
        return self._client[settings.mongo_db_name]


mongo_manager = MongoClientManager()


async def get_database() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    yield mongo_manager.database
