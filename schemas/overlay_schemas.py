from pydantic import BaseModel
from typing import List

from .prediction_schemas import Detection

class OverlayDetection(Detection):
    id: int

class OverlayResponse(BaseModel):
    image_id: str
    image_url: str
    detections: List[OverlayDetection]