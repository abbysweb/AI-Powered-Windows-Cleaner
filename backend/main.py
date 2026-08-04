from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Windows Health Copilot - Backend API")

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Backend is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/advisor")
def advisor(request: PromptRequest):
    # This is a stub for the Ollama integration
    return {"recommendation": f"Received prompt: {request.prompt}", "risk_score": 0}
