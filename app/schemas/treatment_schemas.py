from pydantic import BaseModel


class TreatmentResponse(BaseModel):
    class_id: int
    class_name: str
    title: str
    description: str