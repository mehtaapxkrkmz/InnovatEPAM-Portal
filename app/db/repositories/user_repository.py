from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.user import UserInDB


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["users"]

    async def get_by_email(self, email: str) -> dict | None:
        return await self.collection.find_one({"email": email})

    async def create(self, user: UserInDB | dict) -> dict:
        payload = user.model_dump(by_alias=True) if isinstance(user, UserInDB) else user
        await self.collection.insert_one(payload)
        return payload
