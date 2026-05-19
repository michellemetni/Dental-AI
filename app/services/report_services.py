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

        # If no treatment found (manual annotation or unknown class),
        # tell Llama to use its clinical knowledge
        if not treatment:
            treatment = f"No predefined treatment available for '{d['class_name']}'. Use clinical knowledge to recommend appropriate treatment based on the finding name."

        enriched.append({
            "anomaly": d["class_name"],
            "confidence": d["confidence"],
            "treatment": treatment
        })

    return enriched

def build_prompt(anomalies):
    text = "\n".join([
        f"- {a['anomaly']}" + (f" (confidence: {round(a['confidence'], 2)})" if a.get('confidence') is not None else " (confirmed by dentist)") + f": {a['treatment']}"
        for a in anomalies
    ])

    total = len(anomalies)
    manual = [a for a in anomalies if a.get('confidence') is None]
    ai_detected = [a for a in anomalies if a.get('confidence') is not None]

    return f"""
You are an experienced dental radiologist writing a formal clinical report.

The following {total} anomalies have been CONFIRMED and ARE PRESENT in this dental X-ray ({len(ai_detected)} detected by AI analysis, {len(manual)} confirmed by the examining dentist):

{text}

Rules:
- Do NOT add titles or headings of any kind
- Do NOT use markdown formatting like **, *, #, or any other symbols
- Do NOT add bullet points or numbered lists
- Do NOT repeat the section names "Diagnosis:" or "Treatment Plan:" in your response
- Do NOT mention AI, confidence levels, or percentages in the report text
- Do NOT use first-person ("I", "we", or "our")
- Write in plain paragraph text only
- Every finding listed IS present — NEVER say anything is not detected
- Items marked "confirmed by dentist" are clinically confirmed findings
- Write in formal clinical language
- Do NOT include any preamble, introduction, or phrases like "Here is the report:", "Here is the diagnosis:", "Based on the findings:" or any similar opening phrases
- Start the Diagnosis section directly with the clinical content
- Start the Treatment Plan section directly with the clinical content

Generate the following two sections with DETAILED, SPECIFIC clinical writing. Each section must be at least 3-4 sentences long:

Diagnosis:
Write a thorough clinical diagnosis that mentions each type of anomaly found, their clinical significance, their likely location or distribution across the dental arch, and any relationships between findings. Be specific and detailed.

Treatment Plan:
Write a comprehensive treatment plan that addresses each confirmed finding with specific clinical recommendations, prioritization of urgent treatments, and follow-up care. Be specific about what procedures are needed and why.
"""


def parse_report(response: str):
    preambles = [
        "here is the report:", "here is the diagnosis:", "here is the treatment plan:",
        "based on the findings,", "based on the radiographic findings,",
        "here is a concise", "the following is", "below is"
    ]
    
    response_lower = response.lower()
    for p in preambles:
        if response_lower.startswith(p):
            response = response[len(p):].strip()
            break
    
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
                "temperature": 0.3,
                "num_predict": 400,
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