import json
import os
from datetime import datetime
from uuid import UUID

from backend.core.domain.detections.entities import DetectionTask, DetectionStatus

REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
KEY_PREFIX = "detection_task:"


def _redis_client():
    import redis
    return redis.from_url(REDIS_URL, decode_responses=True)


def _task_to_dict(task: DetectionTask) -> dict:
    return {
        "id": str(task.id),
        "model_type": task.model_type,
        "status": task.status.value,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "result_image_url": task.result_image_url,
        "error_message": task.error_message,
    }


def _dict_to_task(data: dict) -> DetectionTask:
    return DetectionTask(
        id=UUID(data["id"]),
        model_type=data["model_type"],
        status=DetectionStatus(data["status"]),
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
        result_image_url=data.get("result_image_url"),
        error_message=data.get("error_message"),
    )


def save_task(task: DetectionTask) -> None:
    """Сохранить задачу в Redis."""
    client = _redis_client()
    key = f"{KEY_PREFIX}{task.id}"
    client.set(key, json.dumps(_task_to_dict(task)))


def get_task(task_id: UUID) -> DetectionTask | None:
    """Получить задачу по id."""
    client = _redis_client()
    key = f"{KEY_PREFIX}{task_id}"
    raw = client.get(key)
    if not raw:
        return None
    return _dict_to_task(json.loads(raw))


def mark_processing(task_id: UUID) -> None:
    """Перевести задачу в статус processing."""
    task = get_task(task_id)
    if not task:
        return
    task.status = DetectionStatus.processing
    task.updated_at = datetime.utcnow()
    save_task(task)


def mark_completed(task_id: UUID, result_image_url: str) -> None:
    """Отметить задачу выполненной, сохранить URL результата."""
    task = get_task(task_id)
    if not task:
        return
    task.status = DetectionStatus.completed
    task.updated_at = datetime.utcnow()
    task.result_image_url = result_image_url
    task.error_message = None
    save_task(task)


def mark_failed(task_id: UUID, error_message: str) -> None:
    """Отметить задачу как failed с сообщением об ошибке."""
    task = get_task(task_id)
    if not task:
        return
    task.status = DetectionStatus.failed
    task.updated_at = datetime.utcnow()
    task.error_message = error_message
    task.result_image_url = None
    save_task(task)
