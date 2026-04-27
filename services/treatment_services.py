from db.database import SessionLocal
from repositories.treatment_repo import get_treatment_by_class


def fetch_treatment(class_id: int):
    db = SessionLocal()

    try:
        treatment = get_treatment_by_class(db, class_id)

        if not treatment:
            return None

        return {
            "title": treatment.title,
            "description": treatment.description
        }

    finally:
        db.close()