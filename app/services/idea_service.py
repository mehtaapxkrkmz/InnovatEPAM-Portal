from datetime import datetime, timezone
from uuid import uuid4

from app.models.idea import IdeaCreate, IdeaInDB, IdeaPriority, IdeaRead, IdeaStatus
from app.models.user import CurrentUser, UserRole


class IdeaService:
    def __init__(self, idea_repository) -> None:
        self.idea_repository = idea_repository

    async def create_idea(self, payload: IdeaCreate, current_user: CurrentUser) -> IdeaRead:
        now = datetime.now(timezone.utc)
        idea_in_db = IdeaInDB(
            _id=str(uuid4()),
            title=payload.title,
            description=payload.description,
            category=payload.category,
            priority=payload.priority,
            estimated_budget=payload.estimated_budget,
            status=IdeaStatus.SUBMITTED,
            created_by=str(current_user.email),
            created_at=now,
            attachment_url=payload.attachment_url,
        )

        saved = await self.idea_repository.create(idea_in_db.model_dump(by_alias=True))

        return IdeaRead(
            id=str(saved.get("_id", idea_in_db.id)),
            title=saved.get("title", idea_in_db.title),
            description=saved.get("description", idea_in_db.description),
            category=saved.get("category", idea_in_db.category),
            priority=saved.get("priority", idea_in_db.priority),
            estimated_budget=saved.get("estimated_budget", idea_in_db.estimated_budget),
            status=saved.get("status", idea_in_db.status),
            created_by=saved.get("created_by", idea_in_db.created_by),
            created_at=saved.get("created_at", idea_in_db.created_at),
            attachment_url=saved.get("attachment_url", idea_in_db.attachment_url),
            evaluator_comment=saved.get("evaluator_comment", idea_in_db.evaluator_comment),
        )

    async def get_user_ideas(
        self,
        email: str,
        role: UserRole | str = UserRole.SUBMITTER,
        status: IdeaStatus | None = None,
    ) -> list[IdeaRead]:
        status_value = status.value if status is not None else None
        role_value = role.value if isinstance(role, UserRole) else role
        if role_value in (UserRole.ADMIN.value, UserRole.EVALUATOR.value):
            rows = await self.idea_repository.find_all(status=status_value)
        else:
            rows = await self.idea_repository.find_by_owner(email, status=status_value)
        return [
            IdeaRead(
                id=str(row.get("_id", row.get("id", ""))),
                title=row["title"],
                description=row["description"],
                category=row["category"],
                priority=row.get("priority", IdeaPriority.MEDIUM),
                estimated_budget=row.get("estimated_budget"),
                status=row["status"],
                created_by=row["created_by"],
                created_at=row["created_at"],
                attachment_url=row.get("attachment_url"),
                evaluator_comment=row.get("evaluator_comment"),
            )
            for row in rows
        ]

    async def get_idea_by_id(self, idea_id: str):
        row = await self.idea_repository.get_by_id(idea_id)
        if not row:
            raise ValueError("Idea not found")
        return IdeaRead(
            id=str(row.get("_id")),
            title=row["title"],
            description=row["description"],
            category=row["category"],
            priority=row.get("priority", IdeaPriority.MEDIUM),
            estimated_budget=row.get("estimated_budget"),
            status=row["status"],
            created_by=row["created_by"],
            created_at=row["created_at"],
            attachment_url=row.get("attachment_url"),
            evaluator_comment=row.get("evaluator_comment"),
        )

    async def update_idea_status(
        self,
        idea_id: str,
        status: str,
        user_role: UserRole | str,
        evaluator_comment: str | None = None,
    ):
        role_value = user_role.value if isinstance(user_role, UserRole) else user_role
        if role_value not in [UserRole.ADMIN.value, UserRole.EVALUATOR.value]:
            raise PermissionError("Unauthorized role")

        updated = await self.idea_repository.update_status(
            idea_id,
            status,
            evaluator_comment=evaluator_comment,
        )
        if not updated:
            raise ValueError("Idea not found or update failed")

