from datetime import datetime, timezone
from uuid import uuid4

from app.models.idea import IdeaCreate, IdeaInDB, IdeaRead, IdeaStatus


class IdeaService:
    def __init__(self, idea_repository) -> None:
        self.idea_repository = idea_repository

    async def create_idea(self, payload: IdeaCreate, current_user: dict) -> IdeaRead:
        now = datetime.now(timezone.utc)
        idea_in_db = IdeaInDB(
            _id=str(uuid4()),
            title=payload.title,
            description=payload.description,
            category=payload.category,
            status=IdeaStatus.SUBMITTED,
            created_by=current_user["email"],
            created_at=now,
            attachment_url=payload.attachment_url,
        )

        saved = await self.idea_repository.create(idea_in_db.model_dump(by_alias=True))

        return IdeaRead(
            id=str(saved.get("_id", idea_in_db.id)),
            title=saved.get("title", idea_in_db.title),
            description=saved.get("description", idea_in_db.description),
            category=saved.get("category", idea_in_db.category),
            status=saved.get("status", idea_in_db.status),
            created_by=saved.get("created_by", idea_in_db.created_by),
            created_at=saved.get("created_at", idea_in_db.created_at),
            attachment_url=saved.get("attachment_url", idea_in_db.attachment_url),
        )

    async def get_user_ideas(self, email: str) -> list[IdeaRead]:
        rows = await self.idea_repository.find_by_owner(email)
        return [
            IdeaRead(
                id=str(row.get("_id", row.get("id", ""))),
                title=row["title"],
                description=row["description"],
                category=row["category"],
                status=row["status"],
                created_by=row["created_by"],
                created_at=row["created_at"],
                attachment_url=row.get("attachment_url"),
            )
            for row in rows
        ]
