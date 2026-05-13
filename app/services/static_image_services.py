from pathlib import Path
import cv2
import numpy as np

def draw_static_image(image_path, detections, image_id, output_dir="outputs"):
    Path(output_dir).mkdir(exist_ok=True)

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Image not found or unreadable: {image_path}")

    overlay = image.copy()

    for d in detections:
        mask = np.array(d["mask"], dtype=np.int32)

        # fill mask (semi-transparent green overlay)
        cv2.fillPoly(overlay, [mask], (0, 255, 0))

        # draw contour border
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

    # blend overlay + original image
    result = cv2.addWeighted(overlay, 0.4, image, 0.6, 0)

    output_path = f"{output_dir}/{image_id}.jpg"
    cv2.imwrite(output_path, result)

    return output_path