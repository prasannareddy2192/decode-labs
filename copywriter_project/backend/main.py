"""
main.py
-------
FastAPI backend for Project 2: Automated Copywriting & Tone Transformer.

Flow per request:
  1. Validate inputs (product name not empty, platform supported).
  2. Compile the prompt via prompt_builder.build_prompt().
  3. Call Ollama with the compiled prompt + temperature/top_p settings.
  4. Return the generated copy.

Run locally:
    pip install -r requirements.txt
    ollama pull llama3.2   # if not already pulled
    uvicorn main:app --reload

Then open http://127.0.0.1:8000/
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import ollama

from prompt_builder import build_prompt, PLATFORM_RULES

app = FastAPI(title="DecodeLabs Copywriting Transformer - Project 2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_MODEL = "llama3.2"


class GenerateRequest(BaseModel):
    product_name: str
    platform: str
    tone: str
    # Sensible defaults so the frontend doesn't have to always send these.
    temperature: float = Field(default=0.7, ge=0.0, le=1.5)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)


class GenerateResponse(BaseModel):
    copy: str
    prompt_used: str


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    # --- Validation gate ---
    if not req.product_name or not req.product_name.strip():
        raise HTTPException(status_code=400, detail="Product name cannot be empty.")

    try:
        prompt = build_prompt(req.product_name.strip(), req.platform, req.tone)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": req.temperature,
                "top_p": req.top_p,
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama call failed - is `ollama serve` running and is "
                   f"'{OLLAMA_MODEL}' pulled? ({exc})",
        )

    return GenerateResponse(
        copy=response["message"]["content"],
        prompt_used=prompt,
    )


@app.get("/platforms")
def get_platforms():
    """Lets the frontend dynamically populate the platform dropdown."""
    return {"platforms": list(PLATFORM_RULES.keys())}


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve the frontend (must be last - catches all remaining routes)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")