from pydantic import BaseModel
from typing import List, Optional

class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float]           #[x1, y1, x2, y2]
    mask: Optional[List[List[float]]] = None  #segmentation mask

class PredictionResponse(BaseModel):
    detections: List[Detection]

