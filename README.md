# Decode Labs — Generative AI Internship

Projects completed during my Generative AI Internship at Decode Labs
(Batch 2026, completed). Each project lives in its own folder with a
dedicated README covering its purpose, architecture, tech stack, and
results.

## Projects

| # | Project | Description | Stack |
|---|---------|-------------|-------|
| 1 | [Custom AI Chatbot with Memory](./custom_chatbot_project/) | A chatbot that engineers "memory" on top of a stateless LLM using in-memory session state and FIFO sliding-window pruning. | FastAPI, Ollama |
| 2 | [Automated Copywriting & Tone Transformer](./copywriter_project/) | Generates platform-specific marketing copy (LinkedIn, Instagram, Email) from a product description via dynamic prompt templates and tunable Temperature/Top_P. | FastAPI, Ollama |
| 3 | [Multimodal Image Generation Studio](./image-studio-project/) | Translates natural-language prompts into digital artwork via a text-to-image API, with parameterized resolution/aspect ratio and a 3D animated frontend. | FastAPI, Hugging Face Inference Providers |
| 4 | [Intelligent Code Reviewer & Explainer](./code-reviewer-project/) | A CLI tool that reviews a code file under a strict system-prompt format, producing a bug report and refactored code with syntax-highlighted terminal output. | Python, Ollama, rich |

## What I Learned

Four projects, each building on the last, moving from a single core skill
toward combining all of them:

- **LLMs are stateless by default.** "Memory" in any chatbot is an
  illusion the application layer creates — by resending the full
  conversation history on every call, not something the model does on
  its own. (Project 1)
- **Prompt engineering is a software discipline, not a knack for wording.**
  Structured templates with platform-specific rules baked in, injected
  via variables, produce far more reliable output than ad-hoc prompting.
  (Project 2)
- **Temperature and Top_P are real, testable engineering levers** — low
  temperature produces consistent output across repeated runs, high
  temperature produces genuine variety. Provable by running the same
  prompt twice at each setting and comparing the results directly.
  (Project 2)
- **Binary data is a genuinely different problem from text.** Handling
  images means base64 encoding for safe transport, decoding back into
  something a browser can render, and mapping abstract choices (an
  aspect ratio) to exact technical parameters (pixel dimensions) before
  a request ever goes out. (Project 3)
- **System prompts carry more authority than regular messages.** A
  separate, stricter instruction locks a model into a predictable output
  shape, which matters the moment your code needs to *parse* the
  response rather than just display it. (Project 4)
- **Validation belongs on both sides of the request** — checking user
  input before it reaches the model, and checking the model's output
  before it reaches the user. Every project used this same rejection
  pattern in a different context.
- **Model choice is a real variable, not a footnote.** The same task run
  on a smaller vs. larger local model produced measurably different
  reliability — proven directly in Project 4, where a smaller model
  invented problems in bug-free code while a larger one correctly
  recognized it as clean.
- **The unglamorous parts are the real job.** PowerShell's `curl` alias
  silently failing, virtual environments pointing at the wrong Python,
  git rejecting a push because of unsynced remote history — debugging
  these, not just writing the first working version of a script, is what
  the day-to-day of building software actually looks like.

## About

## About

I'm Prasanna, a final-year Information Technology engineering student
aiming for a career in AI engineering. This repository documents my
Generative AI Internship at Decode Labs, where I built four applied
projects covering session state management, prompt engineering, inference
parameter tuning, multimodal (text-to-image) API integration, and
structured-output validation.

Alongside Generative AI, I also have a computer vision background from a
research internship at NIT Warangal, working on road anomaly detection
(YOLOv8, RT-DETR, U-Net).

**Author:** Sai Prasanna Gedela
**GitHub:** [prasannareddy2192](https://github.com/prasannareddy2192)

**Author:** Sai Prasanna Gedela
**GitHub:** [prasannareddy2192](https://github.com/prasannareddy2192)
