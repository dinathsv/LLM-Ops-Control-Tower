import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from backend.sdk.middleware import ControlTowerMiddleware

app = FastAPI(title="Target LLM Application")

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY", "dummy_key_for_testing")
genai.configure(api_key=API_KEY)

# Initialize the Control Tower Middleware
# Ensure Kafka is running on localhost:9092 via Docker Compose
llm_ops = ControlTowerMiddleware(
    kafka_bootstrap_servers="localhost:9092",
    project_id="prj_alpha",
    app_name="CustomerSupportBot"
)

class QueryRequest(BaseModel):
    prompt: str

@app.post("/ask")
async def ask_llm(request: QueryRequest):
    if API_KEY == "dummy_key_for_testing":
        raise HTTPException(status_code=500, detail="Please set GEMINI_API_KEY environment variable.")
        
    try:
        # Instead of calling genai directly, we use our middleware wrapper
        response = llm_ops.generate_content(
            model_name="gemini-1.5-flash",
            prompt=request.prompt
        )
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
def shutdown_event():
    # Ensure all telemetry is sent before shutting down
    llm_ops.flush()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
