from database import SessionLocal
from models import TreatmentPlan

def seed_treatment_plans():
    db = SessionLocal()

    plans = [
        TreatmentPlan(
            class_id=1,
            class_name="Deep Caries",
            title="Advanced Dental Restoration",
            description="Treatment typically involves removing all decayed tissue, protecting the pulp if exposed, and restoring the tooth using a filling or crown depending on severity. In severe cases, root canal treatment may be required."
        ),
        TreatmentPlan(
            class_id=2,
            class_name="Caries",
            title="Dental Filling",
            description="Treatment involves removing the decayed portion of the tooth and restoring it using a composite or amalgam filling to prevent further progression and restore normal function."
        ),
        TreatmentPlan(
            class_id=3,
            class_name="Impacted Tooth",
            title="Surgical Extraction of Impacted Tooth",
            description="Treatment usually involves surgical extraction to prevent pain, infection, or damage to adjacent teeth."
        ),
        TreatmentPlan(
            class_id=4,
            class_name="Periapical Lesion",
            title="Endodontic Treatment",
            description="Treatment involves root canal therapy to remove infected tissue and disinfect the canal, or surgical intervention in severe cases."
        ),
    ]

    try:
        for plan in plans:
            db.add(plan)

        db.commit() 
        print("Treatment plans seeded successfully.")

    except Exception as e:
        db.rollback()
        print("Error seeding:", e)

    finally:
        db.close() 

if __name__ == "__main__":
    seed_treatment_plans()