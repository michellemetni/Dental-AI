# take detections , fetches treatment plan from db, merge detections and treatment,
# builds a good prompt, call ollama,  return a structured result.

from uuid import UUID

import requests
from db.database import SessionLocal
from services.treatment_services import fetch_treatment
from services.static_image_services import draw_static_image
from repositories.analysis_repo import get_analysis_by_id

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def clean_detections(detections):
    cleaned = []

    for d in detections:
        cleaned.append({
            "class_id": d["class_id"],
            "class_name": d["class_name"],
            "confidence": d["confidence"]
        })

    return cleaned

def enrich_anomalies(detections):
    enriched = []

    for d in detections:
        treatment = fetch_treatment(d["class_id"])

        enriched.append({
            "anomaly": d["class_name"],
            "confidence": d["confidence"],
            "treatment": treatment
        })

    return enriched


def build_prompt(anomalies):
    text = "\n".join([
        f"- {a['anomaly']}" + (f" (confidence: {round(a['confidence'], 2)})" if a.get('confidence') is not None else "") + f": {a['treatment']}"
        for a in anomalies
    ])

    return f"""
You are a dental radiology assistant.

Analyze the following detected anomalies from a dental X-ray:

{text}

Generate ONLY:

Diagnosis:
(write a concise professional diagnosis including confidence levels where available)

Treatment Plan:
(write a concise professional treatment recommendation)

Rules:
- Do NOT add titles
- Do NOT add bullet points
- Do NOT mention AI
- Be concise and professional  
- Base everything ONLY on the provided anomalies
- Do NOT use first-person language such as "I", "we", or "our"
- if Confidence level is NUll it means its the dentist's annotation, so treat it as it is there.
"""


def parse_report(response: str):
    parts = response.split("Treatment Plan:")

    diagnosis = parts[0].replace("Diagnosis:", "").strip()

    treatment_plan = parts[1].strip() if len(parts) > 1 else ""

    return diagnosis, treatment_plan

def call_llama(prompt: str):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3
            }
        }
    )

    response.raise_for_status()
    return response.json()["response"]

def generate_report(image_id: str):

    print("Generating report for image_id:", image_id)

    image_id = UUID(image_id)

    # 1. create DB session INSIDE service
    db = SessionLocal()

    try:
        # 2. fetch detections
        records = get_analysis_by_id(db, image_id)

        if not records:
            raise ValueError("No analysis found for this image")

        # 3. build detections
        detections = [
            {
                "class_id": r.class_id,
                "class_name": r.class_name,
                "confidence": r.confidence,
                "bbox": r.bbox,
                "mask": r.mask
            }
            for r in records
        ]

        # 4. get image path (via relationship OR query)
        from db.models import Image
        img = db.query(Image).filter(Image.id == image_id).first()
        image_url = img.image_url

        draw_payload = {
            "image_url": image_url,
            "detections": detections,
            "image_id": str(image_id)
        }

        # 5. draw image
        output_path = draw_static_image(
            image_path=image_url,
            detections=detections,
            image_id=image_id
        )

        # 6. LLM pipeline
        clean = clean_detections(detections)
        enriched = enrich_anomalies(clean)

        prompt = build_prompt(enriched)
        response = call_llama(prompt)

        diagnosis, treatment_plan = parse_report(response)

        return {
            "title": "Dental X-ray Analysis Report",
            "image_url": f"/outputs/{image_id}.jpg",
            "diagnosis": diagnosis,
            "treatment_plan": treatment_plan
        }

    finally:
        db.close()