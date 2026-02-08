from __future__ import annotations

from typing import Optional
from uuid import UUID

from backend.core.domain.detections.entities import DetectionTask
from backend.core.infrastructure.task_store import get_task as get_task_from_store


async def get_detection(task_id: UUID) -> Optional[DetectionTask]:
    """Получение задачи детекции по идентификатору из Redis."""
    return get_task_from_store(task_id)

