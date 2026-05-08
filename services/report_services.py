# take detections , fetches treatment plan from db, merge detections and treatment,
# builds a good prompt, call ollama,  return a structured result.

import requests
from services.treatment_services import fetch_treatment
from services.static_image_services import draw_static_image

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
        f"- {a['anomaly']} (confidence: {round(a['confidence'], 2)}): {a['treatment']}"
        for a in anomalies
    ])

    return f"""
You are a dental radiology assistant.

Analyze the following detected anomalies from a dental X-ray:

{text}

Generate ONLY:

Diagnosis:
(write a concise professional diagnosis including confidence levels)

Treatment Plan:
(write a concise professional treatment recommendation)

Rules:
- Do NOT add titles
- Do NOT add bullet points
- Do NOT mention AI
- Be concise and professional  
- Base everything ONLY on the provided anomalies
- Do NOT use first-person language such as "I", "we", or "our"
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


def generate_report(payload):

    draw_static_image(payload)

    detections = payload["detections"]
    image_id = payload["image_id"]

    clean = clean_detections(detections)

    enriched = enrich_anomalies(clean)

    prompt = build_prompt(enriched)

    print("Calling llama")

    response = call_llama(prompt)

    diagnosis, treatment_plan = parse_report(response)

    return {
        "title": "Dental X-ray Analysis Report",
        "image_url": f"outputs/{image_id}.jpg",
        "diagnosis": diagnosis,
        "treatment_plan": treatment_plan
    }