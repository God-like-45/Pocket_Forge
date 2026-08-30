from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "pocketforge",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

if settings.CELERY_BROKER_URL and settings.CELERY_BROKER_URL.startswith("rediss://"):
    import ssl
    celery_app.conf.broker_use_ssl = {
        'ssl_cert_reqs': ssl.CERT_NONE
    }
    celery_app.conf.redis_backend_use_ssl = {
        'ssl_cert_reqs': ssl.CERT_NONE
    }
