from __future__ import annotations

from fastapi import UploadFile

from backend.core.domain.detections.entities import DetectionTask
from backend.core.infrastructure.task_store import save_task


async def start_detection(file: UploadFile, model_type: str) -> DetectionTask:
    """
    Юз-кейс создания задачи детекции.

    Создаёт сущность, сохраняет в Redis. Сохранение файла на диск и
    отправка задачи в Celery выполняются в API-слое после возврата.
    """
    task = DetectionTask.create(model_type=model_type)
    save_task(task)
    return task

