import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3",
        "prompt": "Write a dental X-ray report for caries",
        "stream": False
    }
)

print(response.json())
