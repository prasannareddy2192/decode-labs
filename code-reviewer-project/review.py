"""
review.py
----------
CLI entry point for Project 4: Intelligent Code Reviewer & Explainer.

Usage:
    python review.py path/to/file.py

Flow:
  1. Read the target file into a string (the "ingest payload" step).
  2. Send it to Ollama with the strict SYSTEM_PROMPT rulebook.
  3. Validate the response has both required sections.
  4. Render the result with rich, so code blocks get syntax highlighting.
"""

import argparse
import os
import sys

import ollama
from rich.console import Console
from rich.markdown import Markdown

from prompts import SYSTEM_PROMPT, build_user_prompt
from validator import validate_response, split_sections, MalformedResponseError

OLLAMA_MODEL = "qwen2.5:7b"

SUPPORTED_EXTENSIONS = {".py", ".js", ".java"}

console = Console()


def read_code_file(path: str) -> str:
    """Step 1: Ingest the raw code file as a string."""
    if not os.path.isfile(path):
        console.print(f"[bold red]Error:[/bold red] File not found: {path}")
        sys.exit(1)

    ext = os.path.splitext(path)[1]
    if ext not in SUPPORTED_EXTENSIONS:
        console.print(
            f"[bold yellow]Warning:[/bold yellow] '{ext}' is not one of the "
            f"officially supported extensions ({', '.join(SUPPORTED_EXTENSIONS)}). "
            f"Proceeding anyway."
        )

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        console.print("[bold red]Error:[/bold red] File is empty.")
        sys.exit(1)

    return content


def review_code(code: str, filename: str) -> str:
    """Step 2: Send the code to Ollama with the strict system prompt."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(code, filename)},
    ]

    with console.status("[bold cyan]Reviewing code...[/bold cyan]"):
        response = ollama.chat(model=OLLAMA_MODEL, messages=messages)

    return response["message"]["content"]


def main():
    parser = argparse.ArgumentParser(
        description="Intelligent Code Reviewer & Explainer - analyzes a "
                     "code file and returns a bug report + refactored version."
    )
    parser.add_argument("file", help="Path to the code file to review (.py, .js, .java)")
    args = parser.parse_args()

    code = read_code_file(args.file)
    filename = os.path.basename(args.file)

    raw_response = review_code(code, filename)

    # Step 3: Validate before showing anything to the user.
    try:
        validate_response(raw_response)
    except MalformedResponseError as exc:
        console.print(f"[bold red]Rejected:[/bold red] {exc}")
        console.print("\n[dim]Raw model output for debugging:[/dim]")
        console.print(raw_response)
        sys.exit(1)

    sections = split_sections(raw_response)

    # Step 4: Render with rich - this is what gives us syntax highlighting.
    console.rule(f"[bold]Code Review: {filename}[/bold]")
    console.print(Markdown(sections["bug_report"]))
    console.print()
    console.print(Markdown(sections["refactored_code"]))
    console.rule()


if __name__ == "__main__":
    main()