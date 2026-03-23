#this file converts to API format and calls the model's predict function

from models.anomalies import DentalModel
from PIL import Image
from schemas.prediction_schemas import PredictionResponse, Detection
from typing import List

dental_model = DentalModel("weights/best.pt")

def predict_image(image_path: str) -> PredictionResponse:
    image = Image.open(image_path)
    raw_results = dental_model.predict(image)

    detections = [Detection(**det) for det in raw_results["detections"]]
    
    return PredictionResponse(detections=detections)