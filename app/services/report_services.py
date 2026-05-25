# take detections , fetches treatment plan from db, merge detections and treatment,
# builds a good prompt, call ollama,  return a structured result.

from uuid import UUID

import requests
from db.database import SessionLocal
from services.treatment_services import fetch_treatment
from services.static_image_services import draw_static_image
from repositories.analysis_repo import get_analysis_by_id

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

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

        if not treatment:
            treatment = f"No predefined treatment available for '{d['class_name']}'. Use clinical knowledge to recommend appropriate treatment based on the finding name."

        enriched.append({
            "anomaly": d["class_name"],
            "confidence": d["confidence"],
            "treatment": treatment
        })

    return enriched

def build_prompt(anomalies):
    # group anomalies by type to avoid repeating
    from collections import Counter
    counts = Counter(a["anomaly"] for a in anomalies)
    summary_lines = []
    seen = set()
    for a in anomalies:
        name = a["anomaly"]
        if name not in seen:
            seen.add(name)
            count = counts[name]
            label = f"{count}x {name}" if count > 1 else name
            confirmed = " (confirmed by dentist)" if a.get("confidence") is None else ""
            summary_lines.append(f"- {label}{confirmed}: {a['treatment']}")

    text = "\n".join(summary_lines)
    total_types = len(seen)

    return f"""You are a dental radiologist. Write a short clinical report with exactly two sections.

Confirmed findings ({total_types} types):
{text}

STRICT RULES:
- Write ONLY two sections: Diagnosis and Treatment Plan
- Each section is exactly 3 sentences
- Do NOT use markdown, bullet points, or bold text
- Do NOT mention confidence levels or AI
- Do NOT use first person
- Do NOT add any preamble or intro text
- Use formal clinical language
- In the Treatment Plan section, address each finding type separately with its specific recommended treatment
- Do NOT use a global treatment plan — each anomaly type must have its own treatment sentence

Diagnosis:
[Write exactly 3 sentences summarizing all findings and their overall clinical significance]

Treatment Plan:
[For each anomaly type found, write one sentence describing the specific treatment. Example: "The fillings require... The impacted tooth requires... The caries require..."]"""


def parse_report(response: str):
    import re

    # split on Treatment Plan header
    parts = re.split(r'(?i)\n\s*treatment\s*plan\s*:?\s*\n', response)

    if len(parts) < 2:
        # fallback — try splitting without newline requirement
        parts = re.split(r'(?i)treatment\s*plan\s*:?', response)

    diagnosis = parts[0].strip()
    # remove Diagnosis header if present
    diagnosis = re.sub(r'(?i)^diagnosis\s*:?\s*\n?', '', diagnosis).strip()
    diagnosis = re.sub(r'\[.*?\]', '', diagnosis).strip()

    treatment_plan = parts[1].strip() if len(parts) > 1 else ""
    treatment_plan = re.sub(r'\[.*?\]', '', treatment_plan).strip()

    return diagnosis, treatment_plan
def call_llama(prompt: str):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 600,
            }
        }
    )

    response.raise_for_status()
    raw = response.json()["response"]
    print("=== RAW LLAMA RESPONSE ===")
    print(raw)
    print("=== END RAW RESPONSE ===")
    return raw

def generate_report(image_id: str):

    print("Generating report for image_id:", image_id)

    image_id = UUID(image_id)

    db = SessionLocal()

    try:
        records = get_analysis_by_id(db, image_id)

        if not records:
            raise ValueError("No analysis found for this image")

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

        from db.models import Image
        img = db.query(Image).filter(Image.id == image_id).first()
        image_url = img.image_url

        # draw image
        output_path = draw_static_image(
            image_path=image_url,
            detections=detections,
            image_id=image_id
        )

        # LLM pipeline
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