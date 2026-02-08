import os

from celery import Celery

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
_app: Celery | None = None


def _get_app() -> Celery:
    global _app
    if _app is None:
        _app = Celery(broker=BROKER_URL)
    return _app


def send_detection_task(task_id: str) -> None:
    """Поставить задачу детекции в очередь (worker выполнит)."""
    _get_app().send_task(
        "backend.worker.tasks.run_detection_task",
        args=[task_id],
    )
