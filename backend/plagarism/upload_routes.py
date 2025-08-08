import os
import re
import json
from pathlib import Path
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from plagarism.section_chunker import process_pdf_to_sections, save_sections_as_json
from services.llm import get_gemma_llm  

plag_upload_bp = Blueprint("plagiarism_upload_bp", __name__)

UPLOAD_DIR = "uploads"
RESULT_DIR = "results"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)


# --- Utility: Safe JSON Parsing ---
def safe_json_parse(llm_output):
    """
    Cleans up LLM output and safely parses JSON.
    Removes code fences, extra text, and tries to extract only valid JSON.
    If parsing fails, returns None.
    """
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


# --- Keyword Extraction ---
def extract_keywords_from_sections(sections):
    llm = get_gemma_llm()

    # Remove references section
    filtered_sections = [
        sec for sec in sections if "reference" not in sec["section"].lower()
    ]

    results = []
    for i in range(0, len(filtered_sections), 5):
        batch = filtered_sections[i:i+5]

        batch_text = ""
        for sec in batch:
            batch_text += f"Section: {sec['section']}\nText:\n{sec['text']}\n\n"

        prompt = (
            "You are a research assistant. For each section below, extract:\n"
            "1. **Top 3 most relevant keywords** (single words, directly tied to the section context)\n"
            "2. **Top 3 most relevant key phrases** (multi-word, directly tied to the section context)\n"
            "3. **All important key points** (bullet points, capturing every crucial idea or fact in the section)\n\n"
            "Return ONLY valid JSON in the format:\n"
            "[\n"
            "  {\n"
            '    "section": "section name",\n'
            '    "keywords": ["word1", "word2", "word3"],\n'
            '    "key_phrases": ["phrase1", "phrase2", "phrase3"],\n'
            '    "key_points": ["point 1", "point 2", "point 3"]\n'
            "  }\n"
            "]\n"
            f"Sections:\n{batch_text}"
        )

        response = llm.invoke(prompt)
        parsed = safe_json_parse(response.content)

        if parsed is not None and isinstance(parsed, list):
            results.extend(parsed)
        else:
            for sec in batch:
                results.append({
                    "section": sec["section"],
                    "error": "Failed to parse LLM output for this section",
                    "raw_output": response.content
                })

    return results


# --- Upload Route ---
@plag_upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, filename)
    file.save(file_path)

    try:
        # Step 1: Chunk PDF
        sections = process_pdf_to_sections(file_path)
        chunks_json_path = os.path.join(RESULT_DIR, Path(filename).stem + ".chunks.json")
        save_sections_as_json(sections, chunks_json_path)

        # Step 2: Extract keywords & key points
        keyword_results = extract_keywords_from_sections(sections)
        keywords_json_path = os.path.join(RESULT_DIR, Path(filename).stem + ".keywords.json")
        with open(keywords_json_path, "w", encoding="utf-8") as f:
            json.dump(keyword_results, f, indent=2, ensure_ascii=False)

        return jsonify({
            "message": "File uploaded, chunked, and keywords extracted successfully",
            "pdf_path": file_path,
            "chunks_json": chunks_json_path,
            "keywords_json": keywords_json_path,
            "sections_count": len(sections)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
