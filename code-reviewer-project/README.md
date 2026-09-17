# 🔍 Intelligent Code Reviewer & Explainer

**Project 4 (Optional) · Generative AI Internship · Decode Labs**

A CLI tool that reads a code file, sends it to an LLM under a strict
system-prompt "rulebook," and renders a structured bug report plus a
refactored version of the code — with syntax-highlighted terminal output.

This project was optional (certification requirements were already met
after Project 3); it was completed to add "Code Analysis Pipelines &
Structured Outputs" as a verified skill.

---

## 🎯 Purpose

An LLM given a code file and asked "review this" will produce a different
shape of answer every time — sometimes a friendly paragraph, sometimes a
bulleted list, sometimes no code block at all. That's fine for a chat
interface, but useless for a tool that needs to reliably parse the
response afterward.

This project solves that with a **system prompt** that behaves like a
strict rulebook rather than a conversational request: it locks the model
into exactly two sections (`## BUG_REPORT`, `## REFACTORED_CODE`), and a
validator that rejects the response outright if either section is
missing — rather than showing the user a malformed or incomplete report.

---

## 👥 Who This Is For

- **Solo developers / students** who want a quick second pair of eyes on
  a script before committing it.
- **Small teams without a formal code review process**, as a fast first
  pass before a human reviewer looks at it.
- **Anyone learning a new language** — the bug report + corrected code
  side-by-side is a fast way to see *why* something was wrong, not just
  that it was.

**How it's used:** run `python review.py path/to/file.py` in a terminal →
get a colorized bug report and a corrected version of the code, rendered
directly in the console.

---

## ⚙️ How It Performs

Tested across multiple languages and edge cases:

| Test | Model | Result |
|---|---|---|
| Python file with real bugs (division by zero, `== True` anti-pattern, non-idiomatic loop) | llama3.2 | ✅ Correctly identified all three; refactor was clean |
| JavaScript file with a real bug (`max` initialized to 0, breaks on all-negative arrays) | llama3.2 | ✅ Correctly identified and fixed; no regressions |
| Java file (array index out of bounds) | llama3.2 | ✅ Correctly identified |
| C file (dangling pointer + buffer overflow) | llama3.2 | ✅ Correctly identified |
| JSON file (unsupported extension, logical inconsistency in data) | llama3.2 | Handled gracefully with a warning; proceeded anyway |
| Clean Python file (genuinely no bugs) | llama3.2 | ❌ Invented issues; refactor introduced a real regression |
| Clean Python file (same file) | **qwen2.5:7b** | ✅ Correctly reported "No issues found" |
| Empty file | — | ✅ Rejected before calling the model at all |

**Key finding:** the smaller model (`llama3.2`) is reliable at finding
*real* bugs across every language tested, but unreliable at recognizing
when code is *already correct* — it would rather invent a problem than
report none. Swapping to a larger model (`qwen2.5:7b`) fixed this specific
failure mode. This is a genuine, evidence-backed distinction between
"finding bugs" and "recognizing correctness" as separate capabilities.

---

## 🏗️ Architecture

```
 ┌──────────────┐   read file    ┌──────────────┐   system+user msgs   ┌──────────────┐
 │  Code file    │ ─────────────▶ │  review.py    │ ────────────────────▶ │    Ollama    │
 │ (.py/.js/.java)│                │ (CLI entry)   │                        │ (llama3.2 /  │
 └──────────────┘                └──────┬───────┘ ◀──────────────────── │  qwen2.5:7b) │
                                          │      raw response text        └──────────────┘
                                          ▼
                                  ┌──────────────┐
                                  │ validator.py  │  reject if headers missing
                                  └──────┬───────┘
                                          │  validated, split sections
                                          ▼
                                  ┌──────────────┐
                                  │ rich.markdown │  syntax-highlighted
                                  │   .Markdown   │  terminal rendering
                                  └──────────────┘
```

**Per-run flow:**
1. `read_code_file()` ingests the target file as a string (rejects if
   missing or empty; warns but proceeds if the extension isn't officially
   supported).
2. `review_code()` builds a two-message payload — a `system` message
   holding the strict format rulebook (`prompts.SYSTEM_PROMPT`), and a
   `user` message holding the actual code — and sends it to Ollama.
3. `validate_response()` checks the raw text for both required section
   headers. If either is missing, the run is rejected and the raw output
   shown for debugging, rather than displaying a broken report.
4. `split_sections()` cuts the validated response into its two parts.
5. Both sections are rendered via `rich.markdown.Markdown`, which turns
   the plain `##` headers and fenced code blocks into colored, formatted
   terminal output.

---

## 🛠️ Tech Stack

| Layer            | Technology            | Why                                                     |
|--------------------|--------------------------|-------------------------------------------------------------|
| LLM                 | **Ollama** (`llama3.2`, `qwen2.5:7b`) | Free, fully local inference — no API key/cost      |
| CLI framework       | **argparse**             | Standard library, no extra dependency for a simple CLI     |
| Terminal rendering  | **rich**                 | Renders Markdown (headers, code blocks) as colored terminal output |
| Prompt structure    | Custom `prompts.py`      | Separates the "rulebook" (system prompt) from user input     |
| Output validation   | Custom `validator.py`    | Rejects malformed model output before display                |

---

## 🚀 Setup (Windows / PowerShell)

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install ollama rich
ollama pull llama3.2
```

Run it against any file:

```powershell
python review.py path\to\your_file.py
```

---

## 📡 Usage

```powershell
python review.py sample_code.py
python review.py sample_code.js
python review.py sample_code.java
```

Supported extensions: `.py`, `.js`, `.java` (other extensions proceed with
a warning rather than being blocked).

---

## 📁 Project Structure

```
code-reviewer-project/
├── review.py            # CLI entry point - ties everything together
├── prompts.py           # SYSTEM_PROMPT rulebook + user prompt builder
├── validator.py          # Checks output has both required sections
├── requirements.txt
└── README.md
```

---

## 💡 Key Design Decisions & Limitations

- **Structural validation only** — the validator checks that both
  required *headers* are present, not that the model's *content* is
  correct. This is a deliberate scope boundary matching the brief's
  actual requirement (format compliance), not a claim that output is
  always semantically correct — see the "No issues found" test above.
- **Model choice affects reliability** — this project surfaced a genuine
  trade-off between `llama3.2` (fast, good at finding real bugs) and
  `qwen2.5:7b` (slower, more reliable at recognizing correct code).
- **No AST-based parsing** — the brief's "enterprise blueprint" content
  around semantic/AST parsing was treated as stretch content, consistent
  with every prior project's scope decisions; this version relies on the
  LLM's own code understanding rather than a separate parsing layer.

## 🔮 Possible Future Upgrades

- Retry automatically (once) on a rejected/malformed response before
  giving up, instead of failing immediately
- Batch mode — review every file in a directory in one run
- Confidence scoring per bug report item
- AST-based pre-analysis to catch syntax errors before even calling the
  model (faster failure for genuinely broken code)