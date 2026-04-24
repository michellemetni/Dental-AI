from datetime import datetime
from xmlrpc.client import DateTime

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dentist_id = Column(String)
    image_url = Column(String)
    uploaded_at = Column(String)


class AIAnomaly(Base):
    __tablename__ = "ai_anomalies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id"))

    class_id = Column(Integer)
    class_name = Column(String)
    confidence = Column(Float)

    bbox = Column(JSON)
    mask = Column(JSON)

    created_at = Column(String)  

class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id"))

    class_id = Column(Integer)
    class_name = Column(String)

    bbox = Column(JSON)
    mask = Column(JSON)

    is_valid = Column(Boolean)

    created_at = Column(String)


class TreatmentPlan(Base):
    __tablename__ = "treatment_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)

    class_id = Column(Integer, unique=True, nullable=False)
    class_name = Column(String, nullable=False)

    title = Column(String, nullable=False) #title for the treamtent plan
    description = Column(String, nullable=False) #more details about the treatment plan