import json
import os
import re
import nltk

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

from nltk.tokenize import sent_tokenize


def chunk_sentences(text, min_sent=2, max_sent=3):
    """
    Break text into smaller chunks of 2-3 sentences.
    """
    sentences = sent_tokenize(text)
    chunks = []
    for i in range(0, len(sentences), max_sent):
        chunk = " ".join(sentences[i:i+max_sent])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def create_sentence_chunks(input_file, output_dir="results"):
    """
    Read section-level JSON, split into sentence chunks,
    and save as .subchunks.json
    """
    with open(input_file, "r", encoding="utf-8") as f:
        sections = json.load(f)

    subchunks_data = []
    for section in sections:
        section_name = section.get("section", "Unknown Section")
        text = section.get("text", "")
        sentence_chunks = chunk_sentences(text)

        for idx, chunk in enumerate(sentence_chunks):
            subchunks_data.append({
                "section": section_name,
                "chunk_id": idx + 1,
                "text": chunk
            })

    filename = os.path.basename(input_file).replace(".chunks.json", ".subchunks.json")
    output_path = os.path.join(output_dir, filename)

    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(subchunks_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Sub-chunks saved to {output_path}")
    return subchunks_data
