from sqlalchemy.orm import Session
from db.models import TreatmentPlan

def get_treatment_by_class(db: Session, class_id: int):
    return db.query(TreatmentPlan).filter(
        TreatmentPlan.class_id == class_id
    ).first()