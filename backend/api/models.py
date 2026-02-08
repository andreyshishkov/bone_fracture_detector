from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from backend.core.domain.detections.entities import DetectionStatus


class DetectionTaskRead(BaseModel):
    id: UUID
    status: DetectionStatus
    model_type: str
    created_at: datetime
    updated_at: datetime
    result_image_url: Optional[str] = None
    error_message: Optional[str] = None


class DetectionTaskCreateResponse(BaseModel):
    id: UUID
    status: DetectionStatus
    model_type: str
    created_at: datetime

