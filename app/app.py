import traceback
from unittest import result

from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
from services.annotations_service import save_annotations_service
from services.prediction_services import predict_image, generate_overlay_data
from schemas.prediction_schemas import PredictionResponse
from schemas.overlay_schemas import OverlayResponse
from services.treatment_services import fetch_treatment
from schemas.report_schemas import ReportRequest
from fastapi.responses import FileResponse
from schemas.annotations_schemas import AnnotationSaveRequest
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

UPLOAD_DIR = Path(UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

# ── SECURITY: allowed file types and max size ──
ALLOWED_TYPES = {"image/jpeg", "image/png"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB

# ── SECURITY: restrict CORS to frontend origin only ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


@app.post("/overlay-data", response_model=OverlayResponse)
async def overlay_data(file: UploadFile = File(...)):

    # ── SECURITY: validate file type ──
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG files are accepted")

    # ── SECURITY: validate file size ──
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB")

    # ── SECURITY: sanitize filename ──
    safe_filename = Path(file.filename).name
    file_path = UPLOAD_DIR / safe_filename

    try:
        with open(file_path, "wb") as f:
            f.write(contents)

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
def generate_report_endpoint(payload: ReportRequest):
    result = generate_report(payload.image_id)
    return result


@app.post("/get-static-image")
def get_static_image(payload: dict):
    output_path = draw_static_image(payload)
    return FileResponse(output_path, media_type="image/jpeg")


@app.post("/save-annotations")
def save_annotations(payload: AnnotationSaveRequest, db: Session = Depends(get_db)):
    result = save_annotations_service(
        db=db,
        image_id=payload.image_id,
        annotations=payload.annotations
    )
    return result