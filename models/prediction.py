from abc import ABC
from typing import List, Dict
from PIL import Image
import torch
from ultralytics import YOLO
from .base import ModelStrategy #abstract class
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env
MODEL_PATH = os.getenv("MODEL_PATH")

class DentalModel(ModelStrategy, ABC):

    def __init__(self):
        self.model = YOLO(MODEL_PATH)
        self.model.eval() 

        self.class_names = {0: "Caries", 1: "Crown", 2: "Filling", 
                            3: "Implant", 4: "Malaligned", 5: "Mandibular Canal", 
                            6: "Missing teeth", 7: "Periapical lesion", 8: "Retained root", 
                            9: "Root Canal Treatment", 10: "Root Piece", 11: "Impacted tooth", 
                            12: "Maxillary sinus", 13: "Bone Loss", 14: "Fracture teeth", 
                            15: "Permanent Teeth", 16: "Supra Eruption", 17: "TAD",
                            18: "Abutment", 19: "Attrition", 20: "Bone defect",
                            21: "Gingival former", 22: "Metal band", 23: "Orthodontic brackets",
                            24: "Permanent retainer", 25: "Post-core", 26: "Plating",
                            27: "Wire", 28: "Cyst", 29: "Root resorption", 30: "Primary teeth"
            }

    def postprocess(self, results):
        detections = []

        if results and results[0].boxes is not None:
            # Iterate over each detected box
            for i in range(len(results[0].boxes)):
                box = results[0].boxes.xyxy[i].tolist()  # [x1, y1, x2, y2]
                conf = float(results[0].boxes.conf[i])
                cls_id = int(results[0].boxes.cls[i])

                det = {
                    "class_id": cls_id,
                    "class_name": self.class_names.get(cls_id, "Unknown"),
                    "confidence": conf,
                    "bbox": box
                }

                # Add mask if present
                if hasattr(results[0], "masks") and results[0].masks is not None:
                    det["mask"] = results[0].masks.xy[i].tolist()

                detections.append(det)

        return detections

    def predict(self, image: Image.Image) -> Dict:

        with torch.no_grad():
            outputs = self.model(image)

        # Convert raw outputs into JSON-friendly format
        results = self.postprocess(outputs)

        # Return as a dictionary, ready to be sent as JSON via FastAPI
        return {"detections": results}