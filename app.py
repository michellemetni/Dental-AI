import traceback


from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
from services.prediction_services import predict_image, generate_overlay_data
from schemas.prediction_schemas import PredictionResponse
from schemas.overlay_schemas import OverlayResponse
from services.treatment_services import fetch_treatment
import shutil
from pathlib import Path
import os

load_dotenv()
UPLOAD_DIR = os.getenv("UPLOAD_DIR")

app = FastAPI(title="Dental X-ray Detection API")

#to temporarly store uploaded files for now
UPLOAD_DIR = Path(UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

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