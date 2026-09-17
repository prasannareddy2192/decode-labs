"""
image_gen.py
-------------
Wraps the Hugging Face Inference Providers text-to-image API.

Concept: we send a text prompt + size parameters, and the API runs a
diffusion model (FLUX.1-schnell) on Hugging Face's GPU infrastructure,
returning a finished image. We never run the model ourselves.
"""

import os
import io
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()  # reads HF_TOKEN from .env

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError(
        "HF_TOKEN not found. Make sure backend/.env contains HF_TOKEN=hf_..."
    )

client = InferenceClient(provider="auto", api_key=HF_TOKEN)

# FLUX.1-schnell is fast and works well within free-tier rate limits.
MODEL = "black-forest-labs/FLUX.1-schnell"

# Common aspect ratios mapped to actual pixel dimensions.
ASPECT_RATIOS = {
    "1:1": (1024, 1024),
    "16:9": (1344, 768),
    "9:16": (768, 1344),
    "4:3": (1152, 896),
}


def generate_images(prompt: str, aspect_ratio: str, count: int) -> list[bytes]:
    """
    Generate `count` images for the given prompt/aspect ratio.
    Returns a list of raw PNG bytes (one per image).
    """
    if aspect_ratio not in ASPECT_RATIOS:
        raise ValueError(
            f"Unsupported aspect ratio '{aspect_ratio}'. "
            f"Choose from: {', '.join(ASPECT_RATIOS.keys())}"
        )

    width, height = ASPECT_RATIOS[aspect_ratio]
    images_bytes = []

    for _ in range(count):
        # Returns a PIL.Image object
        image = client.text_to_image(
            prompt,
            model=MODEL,
            width=width,
            height=height,
        )

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        images_bytes.append(buffer.getvalue())

    return images_bytes