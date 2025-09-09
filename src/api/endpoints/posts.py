import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, models, schemas
from src.api import deps
from src.tasks.post_tasks import publish_post

router = APIRouter()

@router.post("/", response_model=schemas.ScheduledPost)
async def schedule_post(
    *,
    db: AsyncSession = Depends(deps.get_db),
    post_in: schemas.ScheduledPostCreate,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Schedule a new post for one or more profiles.
    """
    # Create the post and its target associations in the database
    post = await crud.post.create_with_targets(db=db, obj_in=post_in, user_id=current_user.id)

    # Enqueue the Celery task to be executed at the scheduled time
    task = publish_post.apply_async(
        args=[str(post.id)],
        eta=post.scheduled_at
    )

    # Save the Celery task ID to the database record
    await crud.post.update_task_id(db=db, post_id=post.id, task_id=task.id)

    return post

@router.get("/", response_model=List[schemas.ScheduledPost])
async def read_posts(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Retrieve posts for the current user.
    """
    """
    Retrieve posts for the current user.
    """
    posts = await crud.post.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return posts
