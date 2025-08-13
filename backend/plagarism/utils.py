"""
Purpose:
--------
Provides utility functions used across plagiarism-related services.

Responsibilities:
-----------------
- Safely parse potentially messy JSON output from LLMs by cleaning
  up code fences, extra text, and extracting valid JSON structures.

Note:
-----
Designed to handle real-world, imperfect model responses.
"""

import re
import json

def safe_json_parse(llm_output):
    text = llm_output.strip()
    text = re.sub(r"^```(json)?", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"```$", "", text.strip())

    match = re.search(r"\[.*\]|\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
