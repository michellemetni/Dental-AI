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


def build_prompt(anomalies, image_id):
    text = "\n".join([
        f"- {a['anomaly']} (confidence: {round(a['confidence'], 2)}): {a['treatment']}"
        for a in anomalies
    ])

    image_path = f"outputs/{image_id}.jpg"

    return f"""
You are a dental radiology assistant.

Analyze the following detected anomalies from a dental X-ray:

{text}

Generate a report STRICTLY in the following Markdown format:

<center>

# Dental X-ray Analysis Report 

</center>

![X-ray]({image_path})

## Diagnosis

Write a concise diagnosis that includes the detected conditions AND their confidence levels.
Use professional medical language.

## Recommended Treatment Plan

Write a clear and professional treatment plan based on the diagnosis.

Rules:
- Follow the exact Markdown structure above
- Do NOT add extra sections
- Do NOT include patient information
- Do NOT mention AI or detection systems
- Be concise and professional
- Base everything ONLY on the provided anomalies
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


def generate_report(data, image_id):
    clean= clean_detections(data)
    enriched = enrich_anomalies(clean)
    prompt = build_prompt(enriched,image_id)
    print("Calling the llama")
    report = call_llama(prompt)
    return {
        "anomalies": enriched,
        "report": report
    }