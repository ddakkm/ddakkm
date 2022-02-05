import os

from celery import Celery

CELERY_BROKER_URL = os.getenv("REDISSERVER", "redis://redis_server:6379")
CELERY_RESULT_BACKEND = os.getenv("REDISSERVER", "redis://redis_server:6379")

celery = Celery("celery_tasks", backend=CELERY_BROKER_URL, broker=CELERY_RESULT_BACKEND)