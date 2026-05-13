from pydantic import BaseModel

class ReportRequest(BaseModel):
    image_id: str