from fastapi import FastAPI
from src.core.config import settings
from src.api.endpoints import auth, posts
from src.models.base import Base
from src.core.database import engine

# This is a temporary solution for creating DB tables.
# In a real production environment, a migration tool like Alembic should be used.
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

# API router
api_router = FastAPI()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])

app.mount(settings.API_V1_STR, api_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Social Media Scheduling Platform"}
