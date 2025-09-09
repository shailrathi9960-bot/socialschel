from typing import List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.post import ScheduledPost, PostTarget
from src.schemas.post import ScheduledPostCreate

class CRUDPost(CRUDBase[ScheduledPost, ScheduledPostCreate, ScheduledPostCreate]):
    async def create_with_targets(
        self,
        db: AsyncSession,
        *,
        obj_in: ScheduledPostCreate,
        user_id: uuid.UUID
    ) -> ScheduledPost:
        # Create the main post object
        db_post = ScheduledPost(
            content_text=obj_in.content_text,
            scheduled_at=obj_in.scheduled_at,
            user_id=user_id,
        )
        db.add(db_post)

        # Create the association objects (PostTarget)
        for profile_id in obj_in.target_profile_ids:
            target = PostTarget(post=db_post, profile_id=profile_id)
            db.add(target)

        # We need to commit to get the post ID for the Celery task.
        await db.commit()
        await db.refresh(db_post)
        return db_post

    async def update_task_id(
        self,
        db: AsyncSession,
        *,
        post_id: uuid.UUID,
        task_id: str
    ) -> ScheduledPost:
        post = await self.get(db, id=post_id)
        if post:
            post.celery_task_id = task_id
            db.add(post)
            await db.commit()
            await db.refresh(post)
        return post

    async def get_multi_by_user(
        self, db: AsyncSession, *, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[ScheduledPost]:
        result = await db.execute(
            select(self.model)
            .filter(ScheduledPost.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

post = CRUDPost(ScheduledPost)
