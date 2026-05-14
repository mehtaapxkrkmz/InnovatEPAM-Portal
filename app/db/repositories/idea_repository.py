from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.idea import IdeaInDB


class IdeaRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["ideas"]

    async def create(self, idea: IdeaInDB | dict) -> dict:
        payload = idea.model_dump(by_alias=True) if isinstance(idea, IdeaInDB) else idea
        await self.collection.insert_one(payload)
        return payload

    async def find_by_owner(self, email: str, status: str | None = None) -> list[dict]:
        query: dict = {"created_by": email}
        if status is not None:
            query["status"] = status
        cursor = self.collection.find(query)
        return await cursor.to_list(length=None)

    async def list_by_owner(self, created_by: str) -> list[dict]:
        return await self.find_by_owner(created_by)

    async def get_by_id(self, idea_id: str) -> dict | None:
        return await self.collection.find_one({"_id": idea_id})

    async def find_by_id(self, idea_id: str) -> dict | None:
        return await self.collection.find_one({"_id": idea_id})

    async def find_all(self, status: str | None = None) -> list[dict]:
        query: dict = {}
        if status is not None:
            query["status"] = status
        cursor = self.collection.find(query)
        return await cursor.to_list(length=None)

    async def update_status(
        self,
        idea_id: str,
        status: str,
        evaluator_comment: str | None = None,
        score: int | None = None,
    ) -> bool:
        set_fields: dict[str, object] = {"status": status}
        if evaluator_comment is not None:
            set_fields["evaluator_comment"] = evaluator_comment
        if score is not None:
            set_fields["score"] = score

        result = await self.collection.update_one(
            {"_id": idea_id},
            {"$set": set_fields}
        )
        return result.modified_count > 0
