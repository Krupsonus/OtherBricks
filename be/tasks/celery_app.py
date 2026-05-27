from celery import Celery

from config import settings

celery_app = Celery(
    "otherbricks",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["tasks.price_aggregator", "tasks.email_sender"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
