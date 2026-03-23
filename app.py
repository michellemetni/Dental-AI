from fastapi import FastAPI, UploadFile, File, HTTPException
from services.prediction_services import predict_image
from schemas.prediction_schemas import PredictionResponse
import shutil
from pathlib import Path
import os

app = FastAPI(title="Dental X-ray Detection API")

#to temporarly store uploaded files for now
UPLOAD_DIR = Path("uploads")
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

    finally:
        if file_path.exists():
            os.remove(file_path)