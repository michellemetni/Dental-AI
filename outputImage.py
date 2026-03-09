from ultralytics import YOLO
import cv2
import numpy as np
import json

model = YOLO("best.pt")
image_path = "102.JPG"
image = cv2.imread(image_path)
overlay = image.copy()
results = model("102.JPG")

detections = []
mask_color = (0, 255, 0)  #green
alpha = 0.5  # for transparency

for r in results:

    boxes = r.boxes.xyxy.tolist()
    scores = r.boxes.conf.tolist()
    classes = r.boxes.cls.tolist()

    # Add detections to JSON
    for box, score, cls in zip(boxes, scores, classes):
        detections.append({
            "class_id": int(cls),
            "confidence": float(score),
            "bbox": box
        })

    # Draw segmentation masks
    if r.masks is not None:
        masks = r.masks.xy
        for poly in masks:
            pts = np.array(poly, np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(overlay, [pts], color=mask_color)

# Blend overlay with original image
cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

# Save the final image
cv2.imwrite("segmentation_overlay.jpg", image)
print("Segmentation image saved as segmentation_overlay.jpg")

# Save JSON detections
with open("results.json", "w") as f:
    json.dump(detections, f, indent=2)
print("Detections saved as results.json")