"""
Purpose:
--------
Extracts top keywords, key phrases, and key points from PDF sections
using a Large Language Model (LLM).

Responsibilities:
-----------------
- Filter out unwanted sections (e.g., References).
- Prepare structured prompts for the LLM.
- Parse and validate JSON output from the LLM.
- Return extracted metadata for each section.

Note:
-----
This service does not store results to disk — the calling function is
responsible for saving. It also delegates JSON parsing to `utils.py`.
"""

# Fix imports - remove 'plagarism.' prefix
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.llm import get_gemma_llm
from .utils import safe_json_parse

def extract_keywords_from_sections(sections):
    llm = get_gemma_llm()
    filtered_sections = [s for s in sections if "reference" not in s["section"].lower()]
    results = []

    for i in range(0, len(filtered_sections), 5):
        batch = filtered_sections[i:i+5]
        batch_text = "".join(
            f"Section: {sec['section']}\nText:\n{sec['text']}\n\n" for sec in batch
        )

        prompt = (
            "You are a research assistant. For each section below, extract:\n"
            "1. **Top 3 most relevant keywords**\n"
            "2. **Top 3 most relevant key phrases**\n"
            "3. **All important key points**\n\n"
            "Return ONLY valid JSON in this format:\n"
            "[{\"section\":..., \"keywords\":[], \"key_phrases\":[], \"key_points\":[] }]\n"
            f"Sections:\n{batch_text}"
        )

        try:
            response = llm.invoke(prompt)
            parsed = safe_json_parse(response.content)

            if parsed and isinstance(parsed, list):
                results.extend(parsed)
            else:
                for sec in batch:
                    results.append({
                        "section": sec["section"],
                        "error": "Failed to parse LLM output",
                        "raw_output": response.content
                    })
        except Exception as e:
            for sec in batch:
                results.append({
                    "section": sec["section"],
                    "error": f"LLM error: {str(e)}",
                    "raw_output": ""
                })

    return results