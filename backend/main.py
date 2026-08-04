import ollama
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize the Ollama client targeting the internal docker network host
client = ollama.Client(host='http://ollama:11434')

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
    try:
        # Call the local Ollama instance
        response = client.chat(
            model='llama3.2:1b',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are the AI Windows Health Copilot, an elite Windows maintenance and storage optimization assistant. Be concise, highly professional, and provide safe actionable advice.'
                },
                {
                    'role': 'user',
                    'content': request.prompt
                }
            ]
        )
        return {
            "recommendation": response['message']['content'],
            "risk_score": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
