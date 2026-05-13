from pydantic import BaseModel
from typing import Optional

class AnnotationItem(BaseModel):
    id: Optional[str] = None
    class_id: int
    class_name: str
    confidence: Optional[float] = None
    bbox: list
    mask: list

    is_valid: bool


class AnnotationSaveRequest(BaseModel):
    image_id: str
    annotations: list[AnnotationItem]