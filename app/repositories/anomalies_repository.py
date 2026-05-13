# anomalies_repository_debug.py
from db.models import AIAnomaly
from sqlalchemy.orm import Session
from datetime import datetime
import traceback

def insert_anomalies_debug(session: Session, image_id: str, detections: list):
    """
    Debug version: prints all detections and types before inserting to DB.
    """
    for idx, det in enumerate(detections):
        try:
            print(f"\nProcessing detection #{idx}: {det}")
            print(f"Type: {type(det)}")

            # handle both OverlayDetection objects and dicts
            if hasattr(det, "class_id"):
                print("Detected OverlayDetection object")
                class_id = det.class_id
                class_name = det.class_name
                confidence = det.confidence
                bbox = det.bbox
                mask = det.mask
            elif isinstance(det, dict):
                print("Detected dict")
                class_id = det.get("class_id")
                class_name = det.get("class_name")
                confidence = det.get("confidence")
                bbox = det.get("bbox")
                mask = det.get("mask")
            else:
                raise ValueError(f"Unsupported detection type: {type(det)}")

            print(f"class_id={class_id}, class_name={class_name}, confidence={confidence}")
            print(f"bbox={bbox}, mask={mask}")

            anomaly = AIAnomaly(
                image_id=image_id,
                class_id=class_id,
                class_name=class_name,
                confidence=confidence,
                bbox=bbox,
                mask=mask,
                created_at=datetime.utcnow()
            )
            session.add(anomaly)
            print("Added anomaly to session successfully!")

        except Exception as e:
            print(f"Error processing detection #{idx}: {e}")
            print(traceback.format_exc())
            raise e  # re-raise so we can still catch in the endpoint