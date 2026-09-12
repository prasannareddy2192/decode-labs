"""
prompt_builder.py
------------------
Compiles a dynamic prompt template from user-supplied variables
(Product_Name, Platform, Tone), applying platform-specific constraints
before the instruction ever reaches the model.

This is the "Master Instruction Template" pattern from the brief: raw user
input never goes straight to the model - it's always wrapped in a
structured template that enforces format/length rules per platform.
"""

# Platform-specific rules, baked into the template rather than left to the
# model to guess. This is the "Platform-Specific Filtering" the brief
# describes - conditional constraints appended before the prompt is sent.
PLATFORM_RULES = {
    "LinkedIn": (
        "Write a professional LinkedIn post. Keep it 3-5 short paragraphs, "
        "use a confident and credible tone appropriate for a business "
        "audience, and end with a soft call-to-action. No more than 200 words."
    ),
    "Instagram": (
        "Write a punchy Instagram caption. Keep it short (2-4 sentences), "
        "use an engaging and energetic voice, and include 3-5 relevant "
        "hashtags at the end."
    ),
    "Email": (
        "Write a marketing email. Include a compelling subject line on the "
        "first line prefixed with 'Subject:', followed by a short, "
        "persuasive body (under 150 words) with a clear call-to-action."
    ),
}


def build_prompt(product_name: str, platform: str, tone: str) -> str:
    """
    Compile the final instruction sent to the model.

    Raises ValueError if an unsupported platform is passed - this is the
    "Structural Validation Gate" pattern from Project 1, applied here too.
    """
    if platform not in PLATFORM_RULES:
        raise ValueError(
            f"Unsupported platform '{platform}'. Choose from: "
            f"{', '.join(PLATFORM_RULES.keys())}"
        )

    platform_instruction = PLATFORM_RULES[platform]

    return (
        f"You are an expert marketing copywriter. "
        f"{platform_instruction}\n\n"
        f"Product/Service: {product_name}\n"
        f"Tone: {tone}\n\n"
        f"Write the copy now. Output ONLY the final copy, no explanations "
        f"or preamble."
    )