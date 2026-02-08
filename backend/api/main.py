import os
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from uuid import UUID

from backend.core.application.detections.commands import start_detection
from backend.core.application.detections.queries import get_detection
from backend.api.models import DetectionTaskRead, DetectionTaskCreateResponse
from backend.api.celery_client import send_detection_task

MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", "media"))


def create_app() -> FastAPI:
    app = FastAPI(title="Bone-fracture detection API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    async def health_check():
        return {"status": "ok"}

    @app.post(
        "/api/detections",
        response_model=DetectionTaskCreateResponse,
        status_code=201,
    )
    async def create_detection(
        file: UploadFile = File(...),
        model_type: str = "nano",
    ):
        if file.content_type not in ("image/png", "image/jpeg"):
            raise HTTPException(
                status_code=400,
                detail="Требуется PNG или JPEG изображение",
            )

        task = await start_detection(file=file, model_type=model_type)

        ext = ".png" if file.content_type == "image/png" else ".jpg"
        input_dir = MEDIA_ROOT / "input"
        input_dir.mkdir(parents=True, exist_ok=True)
        input_path = input_dir / f"{task.id}{ext}"
        input_path.write_bytes(await file.read())

        send_detection_task(str(task.id))

        return DetectionTaskCreateResponse(
            id=task.id,
            status=task.status,
            model_type=task.model_type,
            created_at=task.created_at,
        )

    @app.get(
        "/api/detections/{task_id}",
        response_model=DetectionTaskRead,
    )
    async def get_detection_view(task_id: UUID):
        task = await get_detection(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        return task

    @app.get("/api/media/{path:path}", response_class=FileResponse)
    async def serve_media(path: str):
        """Раздача файлов из MEDIA_ROOT (результаты детекции и т.п.)."""
        full_path = (MEDIA_ROOT / path).resolve()
        media_root = MEDIA_ROOT.resolve()
        try:
            full_path.relative_to(media_root)
        except ValueError:
            raise HTTPException(status_code=404, detail="Не найдено")
        if not full_path.is_file():
            raise HTTPException(status_code=404, detail="Не найдено")
        return FileResponse(full_path)

    return app


app = create_app()

