import base64
import binascii
import json

import ollama
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Vision / image-analysis limits and supported signatures.
MAX_IMAGE_BYTES = 10 * 1024 * 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"
WEBP_RIFF_MAGIC = b"RIFF"
WEBP_WEBP_MAGIC = b"WEBP"


def validate_image(image_bytes: bytes) -> None:
    """Rejects empty, oversized or unsupported image payloads.

    Raises ``HTTPException`` on failure. Only PNG, JPEG and WebP are accepted.
    """
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Image data is empty.")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=413, detail="Image exceeds the 10MB size limit."
        )
    is_png = image_bytes.startswith(PNG_MAGIC)
    is_jpeg = image_bytes.startswith(JPEG_MAGIC)
    is_webp = image_bytes.startswith(WEBP_RIFF_MAGIC) and image_bytes[8:12] == WEBP_WEBP_MAGIC
    if not (is_png or is_jpeg or is_webp):
        raise HTTPException(
            status_code=415, detail="Unsupported image format. Use PNG, JPEG or WebP."
        )

# Initialize the Ollama client targeting the internal docker network host
client = ollama.Client(host='http://ollama:11434', timeout=300)

app = FastAPI(title="AI Windows Health Copilot - Backend API")

class PromptRequest(BaseModel):
    prompt: str

class StreamRequest(BaseModel):
    session_id: str | None = None
    messages: list[dict[str, str]]
    model: str = "llama3.2:1b"
    stream: bool = True
    system_prompt: str = 'You are the AI Windows Health Copilot, an elite Windows maintenance and storage optimization assistant. Be concise, highly professional, and provide safe actionable advice.'
    temperature: float = 0.7


class VisionRequest(BaseModel):
    image_base64: str
    prompt: str = "Analyze this image."
    model: str = "llava:7b"
    temperature: float = 0.2

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

@app.post("/api/chat/stream")
def chat_stream(request: StreamRequest):
    try:
        messages = [{"role": "system", "content": request.system_prompt}]
        messages.extend(request.messages)

        def generate():
            stream = client.chat(
                model=request.model,
                messages=messages,
                stream=True,
                temperature=request.temperature,
            )

            usage = {"prompt_tokens": 0, "completion_tokens": 0}
            for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield f"data: {json.dumps({'type': 'token', 'content': content, 'done': False})}\n\n"
                if chunk.get("done"):
                    usage["prompt_tokens"] = chunk.get("prompt_eval_count", 0)
                    usage["completion_tokens"] = chunk.get("eval_count", 0)

            yield f"data: {json.dumps({'type': 'complete', 'content': '', 'done': True, 'usage': usage})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/vision/analyze")
def vision_analyze(request: VisionRequest):
    try:
        try:
            image_bytes = base64.b64decode(request.image_base64, validate=True)
        except (binascii.Error, ValueError):
            raise HTTPException(
                status_code=400, detail="Invalid base64 image data."
            )
        validate_image(image_bytes)

        response = client.generate(
            model=request.model,
            prompt=request.prompt,
            images=[request.image_base64],
            stream=False,
            options={"temperature": request.temperature},
        )
        return {
            "analysis": response.get("response", ""),
            "model": request.model,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
