import os
import uvicorn
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from core.db_models import Base, Trace
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

PG_URI = "sqlite:///./control_tower.db"
engine = create_engine(PG_URI, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LLM Ops Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TraceResponse(BaseModel):
    trace_id: str
    timestamp: datetime
    project_id: str
    application_name: str
    model_version: str
    prompt: str
    response: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    cost_usd: float

    class Config:
        orm_mode = True

@app.get("/api/traces", response_model=List[TraceResponse])
def get_traces(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[str] = None
):
    query = db.query(Trace)
    if project_id:
        query = query.filter(Trace.project_id == project_id)
    traces = query.order_by(Trace.timestamp.desc()).offset(skip).limit(limit).all()
    return traces

@app.get("/api/costs")
def get_costs(db: Session = Depends(get_db)):
    # Aggregate costs by project and model
    results = db.query(
        Trace.project_id,
        Trace.model_version,
        func.sum(Trace.cost_usd).label("total_cost"),
        func.sum(Trace.input_tokens).label("total_input_tokens"),
        func.sum(Trace.output_tokens).label("total_output_tokens"),
        func.count(Trace.trace_id).label("total_requests")
    ).group_by(Trace.project_id, Trace.model_version).all()
    
    return [
        {
            "project_id": row.project_id,
            "model_version": row.model_version,
            "total_cost": row.total_cost,
            "total_input_tokens": row.total_input_tokens,
            "total_output_tokens": row.total_output_tokens,
            "total_requests": row.total_requests
        }
        for row in results
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
