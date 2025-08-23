import os
import json

def load_pdf_chunks(path):
    """Load pre-chunked JSON file from results/ directory."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    chunks = []
    for it in data:
        if isinstance(it, str):
            chunks.append(it.strip())
        elif isinstance(it, dict):
            text = it.get("text") or it.get("content") or it.get("chunk") or ""
            if text:
                chunks.append(text.strip())
    return [c for c in chunks if c]

def load_web_chunks(path="scraped_data/web/web_results.json"):
    """Load scraped web chunks."""
    if not os.path.exists(path):
        print(f"[Warning] web file not found: {path}")
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"[Warning] invalid/empty json: {path}")
        return []
    chunks = []
    for item in data.get("search_results", []):
        content = item.get("content") if isinstance(item, dict) else None
        if content and isinstance(content, str):
            chunks.append(content.strip())
    return [c for c in chunks if c]
