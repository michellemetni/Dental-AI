from db.models import Annotation

def save_annotations_service(db, image_id, annotations):

    #delete old annotations for this image
    db.query(Annotation).filter(
        Annotation.image_id == image_id
    ).delete()

    new_records = []

    for a in annotations:
        record = Annotation(
            image_id=image_id,
            class_id=a.class_id,
            class_name=a.class_name,
            confidence=a.confidence,  # ← add this
            bbox=a.bbox,
            mask=a.mask,
            is_valid=a.is_valid
        )
        db.add(record)
        new_records.append(record)

    db.commit()

    return {
        "message": "annotations saved",
        "count": len(new_records)
    }