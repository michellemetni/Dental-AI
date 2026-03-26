#this file converts to API format
import os
import uuid
from models.prediction import DentalModel
from PIL import Image
from schemas.prediction_schemas import PredictionResponse, Detection
from typing import List
from schemas.overlay_schemas import OverlayResponse, OverlayDetection
from pathlib import Path
from db.database import SessionLocal
from repositories.image_repository import insert_image
from dotenv import load_dotenv

load_dotenv()
UPLOAD_DIR = os.getenv("UPLOAD_DIR")

dental_model = DentalModel("weights/best.pt")

#to temporarly store uploaded files for now
UPLOAD_DIR = Path(UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)


def predict_image(image_path: str) -> PredictionResponse:
    image = Image.open(image_path)
    raw_results = dental_model.predict(image)

    detections = [Detection(**det) for det in raw_results["detections"]]
    
    return PredictionResponse(detections=detections)

def generate_overlay_data(image_path: str) -> OverlayResponse:
    image = Image.open(image_path)
    raw_results = dental_model.predict(image)

    detections = []
    for idx, det in enumerate(raw_results["detections"]): #iterate over each anomaly found and assign a unique id. 
        det_with_id = OverlayDetection(anomaly_id=idx, **det)
        detections.append(det_with_id)

    image_filename = os.path.basename(image_path)
    image_id = str(uuid.uuid4())  # unique id for this X-ray
    image_url = f"{UPLOAD_DIR}/{image_filename}"  # URL for image

    save_prediction_to_db(image_id, image_url, detections)


    response = OverlayResponse(
        image_id=image_id,
        image_url=image_url,
        detections=detections
    )

    return response

def save_prediction_to_db(image_id, image_url, detections, dentist_id="1"):
    session = SessionLocal()
    try:
        insert_image(session, image_id, dentist_id, image_url)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()