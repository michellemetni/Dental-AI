from ultralytics import YOLO
import json

model = YOLO("best.pt")
results = model("102.JPG")

detections = []

for r in results:
    boxes = r.boxes.xyxy.tolist()
    scores = r.boxes.conf.tolist()
    classes = r.boxes.cls.tolist()

    masks = None
    if r.masks is not None:
        masks = r.masks.xy  # polygon points

    for i in range(len(boxes)):

        detection = {
            "class_id": int(classes[i]),
            "confidence": float(scores[i]),
            "bbox": boxes[i]
        }

        if masks is not None:
            detection["segmentation"] = masks[i].tolist()

        detections.append(detection)

# Save JSON
with open("results.json", "w") as f:
    json.dump(detections, f, indent=2)

print("JSON saved as results.json")