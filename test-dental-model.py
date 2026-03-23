from PIL import Image
import torch
from models.anomalies import DentalModel 

# 1. Initialize the model with your .pt file
model_path = "weights/best.pt"
dental_model = DentalModel(model_path)

# 2. Load a sample X-ray image
image_path = "102.JPG"  
image = Image.open(image_path)

# 3. Call predict
results = dental_model.predict(image)

# 4. Print JSON output
import json
print(json.dumps(results, indent=2))