from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class DetectionStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


@dataclass
class DetectionTask:
    id: UUID
    model_type: str
    status: DetectionStatus
    created_at: datetime
    updated_at: datetime
    result_image_url: Optional[str] = None
    error_message: Optional[str] = None

    @classmethod
    def create(cls, model_type: str) -> "DetectionTask":
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            model_type=model_type,
            status=DetectionStatus.queued,
            created_at=now,
            updated_at=now,
        )

