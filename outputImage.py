from ultralytics import YOLO
import cv2
import numpy as np
import json
import random


MODEL_PATH = "best.pt"
IMAGE_PATH = "102.JPG"
OUTPUT_IMAGE = "outputImage.jpg"
OUTPUT_JSON = "results.json"
ALPHA = 0.5  # transparency level for the mask 

model = YOLO(MODEL_PATH) #load the model 


image = cv2.imread(IMAGE_PATH) 
overlay = image.copy()  # a copy of the image for transparency

#colors
num_classes = len(model.names)
random.seed(42)  #so colors stays the same every run 
class_colors = {i: tuple(random.choices(range(50, 256), k=3)) for i in range(num_classes)}


results = model(IMAGE_PATH)

detections = []

for r in results:

    boxes = r.boxes.xyxy.tolist()
    scores = r.boxes.conf.tolist()
    classes = r.boxes.cls.tolist()

    masks = r.masks.xy if r.masks is not None else [None] * len(boxes)

    for i, (box, score, cls) in enumerate(zip(boxes, scores, classes)):
        detection = {
            "class_id": int(cls),
            "class_name": model.names[int(cls)],
            "confidence": float(score),
            "bbox": box
        }

        if masks[i] is not None:
            detection["mask"] = np.array(masks[i]).tolist()  # polygon points

        detections.append(detection)

    # Draw segmentation masks
    if r.masks is not None:
        for poly, cls in zip(r.masks.xy, classes):
            pts = np.array(poly, np.int32).reshape((-1, 1, 2))
            color = class_colors[int(cls)]
            cv2.fillPoly(overlay, [pts], color=color) #drawing masks on the overlay image


cv2.addWeighted(overlay, ALPHA, image, 1 - ALPHA, 0, image) #blend overlay + original image

# Legend
detected_classes = set(int(cls) for r in results for cls in r.boxes.cls.tolist())

for idx, class_id in enumerate(detected_classes):
    color = class_colors[class_id]
    cv2.rectangle(image, (10, 30*idx+10), (30, 30*idx+30), color, -1)
    cv2.putText(image, model.names[class_id], (40, 30*idx+30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


# Save outputs
cv2.imwrite(OUTPUT_IMAGE, image)
print(f"Segmentation image saved as {OUTPUT_IMAGE}")

with open(OUTPUT_JSON, "w") as f:
    json.dump(detections, f, indent=2)

print(f"Detections saved as {OUTPUT_JSON}")
