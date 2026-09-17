# 🎨 Multimodal Image Generation Studio

**Project 3 · Generative AI Internship · Decode Labs**

A text-to-image application that translates natural language descriptions
into digital artwork — bridging human language and synthetic visual
generation through a clean, parameterized API pipeline.

---

## 🎯 Purpose

Generative image models don't take plain requests — they need a text
prompt paired with precise technical parameters (resolution, aspect ratio,
how many variations to produce), and the resulting image comes back as raw
binary data that has to be handled correctly before a user ever sees it.

This project builds that full pipeline: taking a natural-language prompt,
compiling it into a structured API payload with the right dimensions for a
chosen aspect ratio, calling a diffusion model to generate the image(s),
and safely converting the binary response into something a browser can
display and let the user download.

---

## 👥 Who This Is For

- **Designers/marketers** needing quick concept art or visual drafts
  without opening a design tool from scratch.
- **Content creators** who need on-demand illustrations for blogs, social
  posts, or presentations.
- **Developers** learning how to integrate a real text-to-image API into
  an application — the same pattern used by tools like Midjourney's API
  clients or DALL·E-powered apps.

**How it's used:** describe the image you want → pick a shape (aspect
ratio) → pick how many variations → generate → preview and download the
result.

---

## ⚙️ How It Performs

- Generates images correctly sized for 4 different aspect ratios (1:1,
  16:9, 9:16, 4:3), each mapped to specific pixel dimensions rather than
  left to the model to guess.
- Supports generating 1-4 images per request from the same prompt.
- **Validates input** before it reaches the API (empty prompt, unsupported
  aspect ratio, out-of-range count) with clear error messages.
- Handles the full binary image lifecycle: receives raw image data from
  the API, base64-encodes it for safe transport in a JSON response, and
  the frontend decodes it back into a downloadable PNG file — no
  intermediate file storage needed.
- Runs on Hugging Face's free-tier Inference Providers — no cost for
  reasonable usage, though it is rate-limited (unlike Ollama's fully local
  Projects 1 & 2).

---

## 🏗️ Architecture

```
 ┌─────────────┐    POST /generate     ┌──────────────┐   generate_images()   ┌──────────────┐
 │   Frontend   │ ──────────────────────▶ │   FastAPI    │ ──────────────────────▶ │  image_gen   │
 │ (index.html) │                        │   backend    │                        │     .py       │
 └─────────────┘ ◀────────────────────── └──────┬───────┘ ◀────────────────────── └──────────────┘
            { images: [base64, ...] }            │                  raw PNG bytes (per image)
                                                  │
                                                  │ InferenceClient.text_to_image(prompt, width, height)
                                                  ▼
                                          ┌──────────────────┐
                                          │ Hugging Face      │
                                          │ Inference Provider│
                                          │ (FLUX.1-schnell)  │
                                          └──────────────────┘
```

**Per-request flow:**
1. User submits `prompt`, `aspect_ratio`, `count`.
2. Backend validates: reject empty prompt, unsupported aspect ratio, or
   count outside 1-4.
3. `image_gen.generate_images()` maps the aspect ratio to exact
   width/height pixels (`ASPECT_RATIOS` dict) and calls the Hugging Face
   Inference Providers API once per requested image.
4. Each returned image is converted to raw PNG bytes, then base64-encoded
   so it can travel safely inside a JSON response.
5. Frontend decodes each base64 string directly into an `<img>` element
   via a `data:image/png;base64,...` URL, and offers a client-side
   download (base64 → Blob → downloadable PNG) with no server-side file
   storage involved.

---

## 🛠️ Tech Stack

| Layer              | Technology                              | Why                                                    |
|----------------------|--------------------------------------------|------------------------------------------------------------|
| Image generation      | **Hugging Face Inference Providers** (FLUX.1-schnell) | Free tier, no local GPU needed, fast diffusion model |
| Backend                | **FastAPI** (Python)                       | Async, typed, auto-generated API docs                       |
| Validation             | **Pydantic** (`Field` constraints)         | Enforces image count range (1-4) automatically              |
| Credential management  | **python-dotenv**                          | Keeps the Hugging Face token out of source code (`.env`)    |
| Image handling         | **Pillow**                                  | Converts API response into a savable PNG                    |
| Frontend               | HTML/CSS/JS + **Three.js** (r128, via cdnjs) | Zero-build single-page app; ~900-particle WebGL field, served directly by FastAPI |
| Frontend design system  | CSS glassmorphism (`backdrop-filter` blur/saturate), CSS custom properties, CSS Grid/Flexbox | Electric violet / cyber magenta / radiant cyan palette on an obsidian base |
| Typography              | **Plus Jakarta Sans**, **Inter**, **JetBrains Mono** (Google Fonts) | Display headers, UI body text, and technical metadata respectively |
| Icons                   | Inline SVG (Feather/Lucide-inspired)       | No external icon font bundle                                  |
| Server                 | **Uvicorn**                                | ASGI server for FastAPI                                       |

---

## ✨ Frontend Features

- **Interactive 3D particle field** — WebGL constellation of ~900 particles
  in a cylindrical volume, with mouse-parallax tilt (lerp-smoothed) and an
  automatic pause via the Page Visibility API when the tab isn't active.
- **Floating command dock** — auto-resizing prompt input with a "✨ Polish"
  prompt expander and a "🎲 Surprise" randomizer.
- **Adaptive preview stage** — layout shifts between 1-hero, 2-column,
  3-column, or 2×2 grid depending on how many images were requested.
- **Fullscreen lightbox** — light-dismiss modal with zoom and direct PNG
  download.
- **Session history drawer** — a slide-out panel caching generations made
  during the current session.
- **Dual operating mode** — connects live to the FastAPI/FLUX backend when
  available, with a built-in offline "Demo Mode" fallback.

---

## 🚀 Setup (Windows / PowerShell)

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file inside `backend/` containing:
```
HF_TOKEN=hf_your_actual_token_here
```
(Get a free token from huggingface.co → Settings → Access Tokens.)

Then run:
```powershell
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000/**. API docs at `http://127.0.0.1:8000/docs`.

---

## 🧪 Results / Testing

Tested by generating images across all 4 aspect ratios with varied prompts
(architectural scenes, still life, landscapes). Verified:
- Each aspect ratio produces correctly-proportioned output matching its
  intended pixel dimensions (e.g. 16:9 → 1344×768, not a cropped square).
- Requesting `count=3` correctly returns 3 distinct images, generated
  sequentially, all matching the same prompt and aspect ratio.
- Empty prompt correctly rejected with a 400 error before any API call is
  made (no wasted rate-limit usage on invalid requests).
- Generated images render immediately in-browser via base64 data URLs and
  can be downloaded individually as standalone PNG files.

---

## 📡 API Endpoints

| Method | Path              | Purpose                                          |
|--------|---------------------|-----------------------------------------------------|
| POST   | `/generate`         | Generate 1-4 images from a prompt + aspect ratio     |
| GET    | `/aspect-ratios`    | List supported aspect ratios (for dynamic UI)         |
| GET    | `/health`           | Health check                                          |

---

## 📁 Project Structure

```
image-studio-project/
├── backend/
│   ├── main.py            # FastAPI app — /generate endpoint, serves frontend/
│   ├── image_gen.py       # Hugging Face Inference Providers wrapper
│   ├── .env                # HF_TOKEN (never committed — see .gitignore)
│   └── requirements.txt
├── frontend/
│   └── index.html            # Glassmorphic 3D UI (Three.js), command dock, lightbox, history drawer
└── README.md
```

---

## 💡 Key Design Decisions & Limitations

- **Base64 over file storage** — generated images are never saved to disk
  server-side; they're encoded and streamed directly in the API response.
  Simpler for this scope, though it means larger response payloads than a
  URL-based approach would produce.
- **Count capped at 4 per request** — a deliberate guardrail to avoid
  exhausting the free-tier rate limit on Hugging Face's Inference
  Providers.
- **Single model (FLUX.1-schnell)** — chosen for speed within free-tier
  constraints; larger/slower models would likely produce higher-fidelity
  output at the cost of generation time.
- **No persistence** — like Projects 1 & 2, generated images aren't saved
  or logged anywhere; each request is independent.

## 🔮 Possible Future Upgrades

- Persist generated images with their prompts (gallery/history view)
- Add negative prompts and style presets (e.g. "cyberpunk", "watercolor")
- Retry logic with exponential backoff for rate-limit/timeout resilience
  (as outlined in the brief's enterprise-scaling stretch content)
- Automated aesthetic/quality scoring to filter low-quality generations