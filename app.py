import traceback


from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
from services.prediction_services import predict_image, generate_overlay_data
from schemas.prediction_schemas import PredictionResponse
from schemas.overlay_schemas import OverlayResponse
from services.treatment_services import fetch_treatment
from fastapi.responses import FileResponse
from services.static_image_services import draw_static_image
import shutil
from pathlib import Path
import os

from services.report_services import generate_report
from fastapi import Depends
from sqlalchemy.orm import Session
from db.database import get_db

from fastapi.middleware.cors import CORSMiddleware 

from fastapi.staticfiles import StaticFiles

load_dotenv()
UPLOAD_DIR = os.getenv("UPLOAD_DIR")

app = FastAPI(title="Dental X-ray Detection API")

#to temporarly store uploaded files for now
UPLOAD_DIR = Path(UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

#this is added to permit the backend to talk with frontend
app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

# this is to let the outputs folder be accessible to the frontend
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename

    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Call service layer
        result = predict_image(str(file_path))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/overlay-data", response_model=OverlayResponse)
async def overlay_data(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename

    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = generate_overlay_data(str(file_path))
        return result

    except Exception as e:
        print("❌ FULL ERROR TRACEBACK:")
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/treatment/{class_id}")
def get_treatment(class_id: int):
    result = fetch_treatment(class_id)

    if not result:
        return {"error": "Treatment not found"}

    return result

@app.post("/generate-report")
def generate_report_endpoint(payload: dict):

    result = generate_report(payload)

    return result

@app.post("/get-static-image")
def get_static_image(payload: dict):

    output_path = draw_static_image(payload)

    return FileResponse(output_path, media_type="image/jpeg")