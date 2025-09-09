import asyncio
import uuid
from celery import shared_task
from sqlalchemy.future import select

from src.core.database import SessionLocal
from src.models import ScheduledPost

@shared_task(
    bind=True,
    autoretry_for=(Exception,), # In production, use more specific exceptions
    retry_kwargs={'max_retries': 5, 'countdown': 60}
)
async def publish_post(self, post_id: str):
    """
    A Celery task to publish a scheduled post.
    It's designed to be idempotent and resilient to transient errors.
    """
    db_session = SessionLocal()
    try:
        post_uuid = uuid.UUID(post_id)

        # --- Idempotency Check ---
        result = await db_session.execute(
            select(ScheduledPost).filter(ScheduledPost.id == post_uuid)
        )
        post = result.scalars().first()

        if not post:
            print(f"Post with ID {post_id} not found. Aborting task.")
            return

        if post.status != 'scheduled':
            print(f"Post {post_id} is not in 'scheduled' state (current: {post.status}). Aborting task.")
            return

        # --- Mark as Processing ---
        print(f"Processing post {post_id}...")
        post.status = 'processing'
        db_session.add(post)
        await db_session.commit()

        # --- Placeholder for actual publishing logic ---
        # In a real application, this is where you would call the social media API.
        # The logic would fetch credentials from the SocialProfile model and make the API call.
        print(f"Simulating API call for post {post_id}...")
        await asyncio.sleep(5) # Simulate network latency
        print(f"Post {post_id} published successfully (simulated).")

        # --- Update Status to Published ---
        post.status = 'published'
        db_session.add(post)
        await db_session.commit()

    except Exception as exc:
        print(f"Error processing post {post_id}: {exc}")
        # --- Update Status to Failed ---
        if 'post' in locals() and post:
            post.status = 'failed'
            post.error_message = str(exc)
            db_session.add(post)
            await db_session.commit()
        # Re-raise the exception to trigger Celery's retry mechanism
        raise
    finally:
        await db_session.close()
