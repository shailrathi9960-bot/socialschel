from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["src.tasks.post_tasks"]  # Point to the future tasks module
)

celery_app.conf.update(
    task_track_started=True,
)
