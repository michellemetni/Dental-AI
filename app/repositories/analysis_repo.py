from sqlalchemy.orm import Session
from db.models import Annotation
from uuid import UUID

def get_analysis_by_id(db: Session, image_id: UUID):
    return db.query(Annotation).filter(
        Annotation.image_id == image_id
    ).all()