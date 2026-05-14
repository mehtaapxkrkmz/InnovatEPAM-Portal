"""
Review Stage Repository - handles CRUD operations for review stages.
"""

import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.review_stage import (
    ReviewStage,
    ReviewStageCreate,
    ReviewStageEnum,
    ReviewerRole,
)


class ReviewStageRepository:
    """Repository for managing review stages in MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["review_stages"]

    async def ensure_indexes(self):
        """Create necessary MongoDB indexes for review stages."""
        await self.collection.create_index("stage_order", unique=False)
        await self.collection.create_index("stage_name", unique=True)

    async def initialize_default_stages(self):
        """Initialize default review stages if none exist."""
        existing = await self.collection.count_documents({})
        if existing > 0:
            return
        
        default_stages = [
            {
                "_id": str(uuid.uuid4()),
                "stage_name": ReviewStageEnum.TECHNICAL.value,
                "stage_order": 1,
                "description": "Technical feasibility and implementation review",
                "required_approvals": 1,
                "allowed_reviewer_roles": ["technical_lead", "admin"],
                "allow_skip": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            {
                "_id": str(uuid.uuid4()),
                "stage_name": ReviewStageEnum.BUDGET.value,
                "stage_order": 2,
                "description": "Budget and resource allocation review",
                "required_approvals": 1,
                "allowed_reviewer_roles": ["finance", "admin"],
                "allow_skip": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            {
                "_id": str(uuid.uuid4()),
                "stage_name": ReviewStageEnum.LEADERSHIP.value,
                "stage_order": 3,
                "description": "Leadership and strategic alignment review",
                "required_approvals": 1,
                "allowed_reviewer_roles": ["leadership", "admin"],
                "allow_skip": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            {
                "_id": str(uuid.uuid4()),
                "stage_name": ReviewStageEnum.FINAL.value,
                "stage_order": 4,
                "description": "Final approval and decision",
                "required_approvals": 1,
                "allowed_reviewer_roles": ["admin"],
                "allow_skip": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        ]
        
        for stage in default_stages:
            await self.collection.insert_one(stage)

    async def get_all_stages(self) -> list[dict]:
        """Get all review stages sorted by order."""
        stages = await self.collection.find().sort("stage_order", 1).to_list(None)
        return stages or []

    async def get_stage_by_id(self, stage_id: str) -> dict | None:
        """Get a single review stage by ID."""
        return await self.collection.find_one({"_id": stage_id})

    async def get_stage_by_name(self, stage_name: str) -> dict | None:
        """Get a single review stage by name."""
        return await self.collection.find_one({"stage_name": stage_name})

    async def create_stage(self, stage: ReviewStageCreate) -> dict:
        """Create a new review stage."""
        stage_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        doc = {
            "_id": stage_id,
            "stage_name": stage.stage_name,
            "stage_order": stage.stage_order,
            "description": stage.description,
            "required_approvals": stage.required_approvals,
            "allowed_reviewer_roles": stage.allowed_reviewer_roles,
            "allow_skip": stage.allow_skip,
            "created_at": now,
            "updated_at": now,
        }
        
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def update_stage(self, stage_id: str, updates: dict) -> dict | None:
        """Update a review stage."""
        updates["updated_at"] = datetime.utcnow()
        
        result = await self.collection.find_one_and_update(
            {"_id": stage_id},
            {"$set": updates},
            return_document=True,
        )
        return result

    async def delete_stage(self, stage_id: str) -> bool:
        """Delete a review stage."""
        result = await self.collection.delete_one({"_id": stage_id})
        return result.deleted_count > 0

    async def get_next_stage(self, current_stage_order: int) -> dict | None:
        """Get the next review stage after the current one."""
        return await self.collection.find_one(
            {"stage_order": {"$gt": current_stage_order}}
        ).sort("stage_order", 1)
