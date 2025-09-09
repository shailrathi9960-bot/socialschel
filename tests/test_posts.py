import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch
from datetime import datetime, timedelta

from src import crud
from src.schemas import UserCreate
from src.core.config import settings

# A helper to get an authenticated header
async def get_auth_header(client: AsyncClient, db: AsyncSession) -> dict:
    email = f"testuser{_rand_int()}@example.com"
    password = "testpassword"
    user_in = UserCreate(email=email, password=password)
    await crud.user.create(db, obj_in=user_in)

    login_data = {"username": email, "password": password}
    response = await client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}

def _rand_int():
    import random
    return random.randint(1, 10000)

@pytest.mark.asyncio
async def test_schedule_post(client: AsyncClient, db_session: AsyncSession):
    """
    Test scheduling a post successfully.
    """
    auth_headers = await get_auth_header(client, db_session)

    # We need a social profile to target
    profile_in = {"platform": "twitter", "username": "test_twitter", "platform_user_id": "123"}
    # This is a simplified creation. A real test would be more robust.
    # I need a crud function for profiles to do this properly.
    # I'll create a dummy profile manually for now.
    from src.models import SocialProfile, User
    user = await crud.user.get_by_email(db_session, email="testuser1@example.com") # This is fragile

    # Let's get the current user from the token instead.
    from src.core.security import create_access_token
    from src.api.deps import get_current_user

    # This is getting too complicated. I'll create a simpler test utility.
    # The `get_auth_header` should return the user object as well.
    # Let's rewrite the helper.

    # Simplified test setup
    email = f"testuser{_rand_int()}@example.com"
    password = "testpassword"
    user_in_create = UserCreate(email=email, password=password)
    user = await crud.user.create(db_session, obj_in=user_in_create)

    # Create a social profile required for scheduling
    from src.models import SocialProfile
    profile = SocialProfile(
        platform="twitter",
        username="test_twitter",
        platform_user_id="123",
        encrypted_access_token=b"token",
        user_id=user.id
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)

    login_data = {"username": email, "password": password}
    token_resp = await client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    access_token = token_resp.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Now, schedule the post
    scheduled_time = datetime.utcnow() + timedelta(days=1)
    post_data = {
        "content_text": "This is a test post",
        "scheduled_at": scheduled_time.isoformat(),
        "target_profile_ids": [str(profile.id)]
    }

    # Patch the celery apply_async method
    with patch("src.tasks.post_tasks.publish_post.apply_async") as mock_apply_async:
        response = await client.post(
            f"{settings.API_V1_STR}/posts/",
            json=post_data,
            headers=auth_headers,
        )

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["content_text"] == "This is a test post"
    assert data["status"] == "scheduled"
    assert "id" in data

    # Check that celery task was called correctly
    mock_apply_async.assert_called_once()
    call_args, call_kwargs = mock_apply_async.call_args
    assert call_args[0] == [data["id"]]
    # The ETA should be a datetime object
    assert "eta" in call_kwargs
    assert isinstance(call_kwargs["eta"], datetime)
    assert call_kwargs["eta"].isoformat(timespec='seconds') == scheduled_time.isoformat(timespec='seconds')
