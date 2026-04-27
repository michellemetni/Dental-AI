# take detections , fetches treatment plan from db, merge detections and treatment,
# builds a good prompt, call ollama,  return a structured result.

import requests
from services.treatment_services import fetch_treatment

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
    text = ""

    for a in anomalies:
        text += f"""
- Anomaly: {a['anomaly']}
  Confidence: {a['confidence']}%
  Treatment: {a['treatment']}
"""

    return f"""
You are a dental radiology assistant.

Based on the following X-ray analysis:

{text}

Write a structured medical report with:

1. Findings
2. Diagnosis
3. Recommended Treatment Plan

Be concise and professional.
"""


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


# def generate_report(data):
#     detections = clean_detections(data["detections"])
#     enriched = enrich_anomalies(detections)
#     prompt = build_prompt(enriched)
#     report = call_llama(prompt)
#     return {
#         "anomalies": enriched,
#         "report": report
#     }

def generate_report(data):
    clean_detections = clean_detections(data)

    enriched = enrich_anomalies(clean_detections)

    return enriched