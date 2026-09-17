"""
validator.py
-------------
Checks the model's raw response against the strict format required by
prompts.SYSTEM_PROMPT. If either section header is missing, the response
is rejected rather than shown to the user - same validation-gate
philosophy as Projects 1-3, applied here to the MODEL'S output instead of
the user's input.
"""

REQUIRED_HEADERS = ["## BUG_REPORT", "## REFACTORED_CODE"]


class MalformedResponseError(Exception):
    """Raised when the model's response doesn't follow the required format."""
    pass


def validate_response(response_text: str) -> None:
    """
    Raises MalformedResponseError if either required header is missing.
    Does nothing (passes) if the response is well-formed.
    """
    missing = [h for h in REQUIRED_HEADERS if h not in response_text]

    if missing:
        raise MalformedResponseError(
            "Model response is missing required section(s): "
            + ", ".join(missing)
            + ". Refusing to display a malformed report."
        )


def split_sections(response_text: str) -> dict:
    """
    Splits a validated response into its two sections.
    Assumes validate_response() has already confirmed both headers exist.
    """
    bug_start = response_text.index("## BUG_REPORT")
    code_start = response_text.index("## REFACTORED_CODE")

    bug_report = response_text[bug_start:code_start].strip()
    refactored_code = response_text[code_start:].strip()

    return {
        "bug_report": bug_report,
        "refactored_code": refactored_code,
    }