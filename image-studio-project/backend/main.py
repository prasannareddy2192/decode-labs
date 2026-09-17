"""
main.py
-------
FastAPI backend for Project 3: Multimodal Image Generation Studio.

Flow per request:
  1. Validate inputs (prompt not empty, aspect ratio supported, count in range).
  2. Call image_gen.generate_images() to get raw PNG bytes per image.
  3. Base64-encode each image so it can travel inside a JSON response and
     be displayed directly in the browser via a data URL.

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload

Then open http://127.0.0.1:8000/
"""

import base64

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from image_gen import generate_images, ASPECT_RATIOS

app = FastAPI(title="DecodeLabs Image Generation Studio - Project 3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "1:1"
    count: int = Field(default=1, ge=1, le=4)  # cap at 4 to respect free-tier rate limits


class GenerateResponse(BaseModel):
    images: list[str]  # base64-encoded PNGs, ready for <img src="data:image/png;base64,...">


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    # --- Validation gate ---
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    try:
        images_bytes = generate_images(
            prompt=req.prompt.strip(),
            aspect_ratio=req.aspect_ratio,
            count=req.count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Image generation failed - check your HF_TOKEN is valid "
                   f"and you haven't hit the free-tier rate limit. ({exc})",
        )

    encoded = [base64.b64encode(img).decode("utf-8") for img in images_bytes]
    return GenerateResponse(images=encoded)


@app.get("/aspect-ratios")
def get_aspect_ratios():
    return {"aspect_ratios": list(ASPECT_RATIOS.keys())}


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve the frontend (must be last - catches all remaining routes)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")