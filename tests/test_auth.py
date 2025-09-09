import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.schemas import UserCreate
from src.core.config import settings

# A utility to generate random user data
def random_email() -> str:
    import random
    return f"testuser{random.randint(1, 10000)}@example.com"

def random_password() -> str:
    return "somesecurepassword"

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, db_session: AsyncSession):
    """
    Test successful user registration.
    """
    email = random_email()
    password = random_password()
    response = await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert "id" in data

    user = await crud.user.get_by_email(db_session, email=email)
    assert user is not None


@pytest.mark.asyncio
async def test_register_existing_user(client: AsyncClient, db_session: AsyncSession):
    """
    Test that registering a user with an existing email fails.
    """
    email = random_email()
    password = random_password()
    # Create the user first
    user_in = UserCreate(email=email, password=password)
    await crud.user.create(db_session, obj_in=user_in)

    # Try to register again
    response = await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_for_access_token(client: AsyncClient, db_session: AsyncSession):
    """
    Test successful login and token generation.
    """
    email = random_email()
    password = random_password()
    # Create user directly in DB
    user_in = UserCreate(email=email, password=password)
    await crud.user.create(db_session, obj_in=user_in)

    # Attempt to login
    login_data = {"username": email, "password": password}
    response = await client.post(
        f"{settings.API_V1_STR}/auth/token", data=login_data
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_with_bad_password(client: AsyncClient, db_session: AsyncSession):
    """
    Test that login with an incorrect password fails.
    """
    email = random_email()
    password = random_password()
    # Create user directly in DB
    user_in = UserCreate(email=email, password=password)
    await crud.user.create(db_session, obj_in=user_in)

    # Attempt to login with wrong password
    login_data = {"username": email, "password": "wrongpassword"}
    response = await client.post(
        f"{settings.API_V1_STR}/auth/token", data=login_data
    )
    assert response.status_code == 401
