import cv2
import numpy as np
import uuid
from pathlib import Path


def draw_static_image(payload, output_dir="outputs"):
    Path(output_dir).mkdir(exist_ok=True)

    # extract directly from JSON
    image_path = payload["image_url"]
    detections = payload["detections"]

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found")

    overlay = image.copy()

    for d in detections:
        mask = np.array(d["mask"], dtype=np.int32)

        # fill mask
        cv2.fillPoly(overlay, [mask], (0, 255, 0))

        # border
        cv2.polylines(image, [mask], True, (0, 0, 255), 2)

        # label
        x, y = mask[0]
        label = f"{d['class_name']} ({round(d['confidence'], 2)})"
        cv2.putText(
            image,
            label,
            (int(x), int(y) - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )

    result = cv2.addWeighted(overlay, 0.4, image, 0.6, 0)

    output_path = f"{output_dir}/{uuid.uuid4()}.jpg"
    cv2.imwrite(output_path, result)

    return output_path