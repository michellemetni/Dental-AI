#Database Logic
from db.models import Image
from sqlalchemy.orm import Session
from datetime import datetime

def insert_image(session: Session, image_id: str, dentist_id: str, image_url: str):
    img = Image(
        id=image_id,
        dentist_id=dentist_id,
        image_url=image_url,
        uploaded_at=datetime.utcnow()
    )
    session.add(img)