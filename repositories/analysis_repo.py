from sqlalchemy.orm import Session
from db.models import AIAnomaly
from uuid import UUID

def get_analysis_by_id(db: Session, image_id: UUID):
    return db.query(AIAnomaly).filter(
        AIAnomaly.image_id == image_id
    ).all()