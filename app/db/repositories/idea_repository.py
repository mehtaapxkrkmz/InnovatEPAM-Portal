from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.idea import IdeaInDB


class IdeaRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["ideas"]

    async def create(self, idea: IdeaInDB | dict) -> dict:
        payload = idea.model_dump(by_alias=True) if isinstance(idea, IdeaInDB) else idea
        await self.collection.insert_one(payload)
        return payload

    async def find_by_owner(self, email: str) -> list[dict]:
        cursor = self.collection.find({"created_by": email})
        return await cursor.to_list(length=None)

    async def list_by_owner(self, created_by: str) -> list[dict]:
        return await self.find_by_owner(created_by)

    async def get_by_id(self, idea_id: str) -> dict | None:
        return await self.collection.find_one({"_id": idea_id})
