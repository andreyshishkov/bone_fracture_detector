from pathlib import Path
from uuid import UUID

from backend.worker.celery_app import app
from backend.worker.config import MEDIA_ROOT
from backend.core.infrastructure.task_store import (
    get_task,
    mark_processing,
    mark_completed,
    mark_failed,
)
from backend.worker.infrastructure.ml_ultralytics import run_detection as run_ml_detection


@app.task(name="backend.worker.tasks.run_detection_task")
def run_detection_task(task_id: str) -> None:
    """
    Задача детекции по id задачи.

    Читает задачу из Redis, находит входное изображение в MEDIA_ROOT/input/{task_id}.png|.jpg,
    запускает модель, сохраняет результат в MEDIA_ROOT/output/{task_id}.png,
    обновляет задачу в Redis (completed + result_image_url или failed + error_message).
    """
    uid = UUID(task_id)
    task = get_task(uid)
    if not task:
        raise ValueError(f"Задача не найдена: {task_id}")

    input_dir = MEDIA_ROOT / "input"
    input_path = input_dir / f"{task_id}.png"
    if not input_path.exists():
        input_path = input_dir / f"{task_id}.jpg"
    if not input_path.exists():
        mark_failed(uid, "Входной файл изображения не найден")
        return

    output_dir = MEDIA_ROOT / "output"
    output_path = output_dir / f"{task_id}.png"

    mark_processing(uid)

    try:
        run_ml_detection(
            input_path=input_path,
            output_path=output_path,
            model_type=task.model_type,
        )
        result_image_url = f"output/{task_id}.png"
        mark_completed(uid, result_image_url)
    except Exception as e:
        mark_failed(uid, str(e))
        raise
