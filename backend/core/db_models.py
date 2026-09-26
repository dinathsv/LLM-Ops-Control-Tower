from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy import JSON
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class Trace(Base):
    __tablename__ = "traces"
    
    trace_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), index=True)
    project_id = Column(String(50), index=True)
    application_name = Column(String(100))
    model_version = Column(String(50))
    
    prompt = Column(Text)
    response = Column(Text)
    
    latency_ms = Column(Integer)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    cost_usd = Column(Float)
    
    metadata_ = Column("metadata", JSON, default=dict)
    
class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trace_id = Column(String(36), index=True) # Foreign key theoretically, but kept simple
    evaluator_model = Column(String(50))
    rubric_name = Column(String(100))
    score = Column(Float)
    rationale = Column(Text)
    created_at = Column(DateTime(timezone=True))
