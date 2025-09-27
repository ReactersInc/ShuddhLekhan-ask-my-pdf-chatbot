import os
import json
import glob
from pathlib import Path
from nltk.corpus import stopwords
from rapidfuzz import fuzz


STOPWORDS = set(stopwords.words("english"))
import re

def clean_text(text):
    # Remove single-character lines or tokens
    text = re.sub(r'(?m)^[A-Za-z0-9]{1,2}$', '', text)

    # Remove sequences with mostly symbols
    text = re.sub(r'[^A-Za-z\s]{3,}', ' ', text)

    # Collapse newlines/spaces
    text = re.sub(r'\s*\n\s*', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)

    return text.strip()


def clean_subchunks(subchunks, min_words=5, alpha_ratio=0.7):
    cleaned = []
    for s in subchunks:
        txt = clean_text(s.get("text", ""))
        words = txt.split()

        if len(words) < min_words:
            continue

        letters = sum(c.isalpha() for c in txt)
        if letters / max(1, len(txt)) < alpha_ratio:
            continue

        s["text"] = txt
        cleaned.append(s)
    return cleaned
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def is_meaningful(phrase, min_content_words=4):
    """Return True if phrase has enough non-stopwords."""
    words = phrase.split()
    content_words = [w for w in words if w.lower() not in STOPWORDS]
    return len(content_words) >= min_content_words
def merge_overlaps(matches):
    """
    Merge adjacent or overlapping matches based on token index ranges.
    Ensures no repeated words and preserves order.
    """
    if not matches:
        return []

    # Sort matches by start index
    matches = sorted(matches, key=lambda x: x["position"][0])
    merged = [matches[0]]

    for curr in matches[1:]:
        last = merged[-1]
        last_start, last_end = last["position"]
        curr_start, curr_end = curr["position"]

        if curr_start <= last_end:  
            # Overlap detected: merge
            last_tokens = last["overlap_text"].split()
            curr_tokens = curr["overlap_text"].split()

            # Compute overlap region in token indices
            overlap_size = max(0, last_end - curr_start)

            # Add only the non-overlapping part of curr
            merged_text = last_tokens + curr_tokens[overlap_size:]
            merged[-1] = {
                "overlap_text": " ".join(merged_text),
                "length": len(merged_text),
                "position": [last_start, max(last_end, curr_end)]
            }
        else:
            merged.append(curr)

    # Deduplicate based on (text, position)
    unique = []
    seen = set()
    for m in merged:
        clean_text = " ".join(m["overlap_text"].split())
        key = (clean_text, tuple(m["position"]))
        if key not in seen:
            seen.add(key)
            m["overlap_text"] = clean_text
            unique.append(m)

    return unique


def find_overlaps(subchunks, arxiv_text, min_length=8, max_length=12, top_k=3, fuzz_threshold=90):
    """
    Detect meaningful overlapping phrases between subchunks and ArXiv text using fuzzy matching.
    """
    results = []

    for sub in subchunks:
        sub_text = sub.get("text", "")
        sub_words = sub_text.split()

        matches = []
        seen_ngrams = set()

        for n in range(min_length, max_length + 1):
            for i in range(len(sub_words) - n + 1):
                ngram = " ".join(sub_words[i:i+n])
                if not is_meaningful(ngram) or ngram in seen_ngrams:
                    continue
                # Fuzzy match against arxiv_text
                ratio = fuzz.partial_ratio(ngram, arxiv_text)
                if ratio >= fuzz_threshold:
                    matches.append({
                        "overlap_text": ngram,
                        "length": n,
                        "position": [i, i+n]
                    })
                    seen_ngrams.add(ngram)
                    print(f"Found match ({ratio}%): {ngram[:60]}...")  # preview first 60 chars

        # Merge adjacent matches to form longer highlights
        merged = merge_overlaps(matches)

        # Remove overlaps that are substrings of others
        final_overlaps = []
        for m in merged:
            if not any(m["overlap_text"] in other["overlap_text"] and m != other for other in merged):
                final_overlaps.append(m)

        if final_overlaps:
            # Keep top_k longest non-redundant overlaps
            final_overlaps = sorted(final_overlaps, key=lambda x: x["length"], reverse=True)[:top_k]
            results.append({
                "subchunk_id": sub.get("chunk_id"),
                "subchunk_section": sub.get("section_id", "Unknown"),
                "subchunk_text": sub_text,
                "overlaps": final_overlaps
            })

    return results
def filter_overlaps(overlaps, min_chars=12, banned_words=("Figure", "Table")):
    cleaned = []
    for ov in overlaps:
        text = ov["overlap_text"]
        if len(text) < min_chars:
            continue
        if any(b in text for b in banned_words):
            continue
        cleaned.append(ov)
    return cleaned

def run_overlap_pipeline(subchunks_path, arxiv_text_dir="/scraped_data/arxiv/texts",
                         min_length=8, max_length=12, top_k=3, fuzz_threshold=90):
    subchunks = load_json(subchunks_path)
    subchunks = clean_subchunks(subchunks)
    results = {}

    for txt_file in glob.glob(f"{arxiv_text_dir}/*.txt"):
        with open(txt_file, "r", encoding="utf-8") as f:
            arxiv_text = f.read()

        overlaps = find_overlaps(
            subchunks, arxiv_text,
            min_length=min_length,
            max_length=max_length,
            top_k=top_k,
            fuzz_threshold=fuzz_threshold
        )

        # Apply filtering to each subchunk's overlaps
        cleaned_overlaps = []
        for item in overlaps:
            item["overlaps"] = filter_overlaps(item["overlaps"])
            if item["overlaps"]:  # keep only if overlaps remain after filtering
                cleaned_overlaps.append(item)

        if cleaned_overlaps:
            results[Path(txt_file).stem] = cleaned_overlaps

    return results
def run_overlap_for_pdf(subchunks_path, arxiv_text_dir, output_path,
                        min_length=8, max_length=12, top_k=3, fuzz_threshold=90):
    """
    Wrapper for running overlap detection on a user-uploaded PDF
    against all ArXiv texts. Saves the results to output_path.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    results = run_overlap_pipeline(
        subchunks_path=subchunks_path,
        arxiv_text_dir=arxiv_text_dir,
        min_length=min_length,
        max_length=max_length,
        top_k=top_k,
        fuzz_threshold=fuzz_threshold
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("✅ Overlap results saved to:", output_path)
    return results

# if __name__ == "__main__":
#     subchunks_file = "results/Maulik_A_Plagiarism_Detection_Tool_for_Hindi.subchunks.json"
#     arxiv_text_dir = "../scraped_data/arxiv/texts"
#     out_path = "comparison/Maulik_A_Plagiarism_Detection_Tool_for_Hindi_overlap_pdf_only.json"
#     os.makedirs(os.path.dirname(out_path), exist_ok=True)

#     results = run_overlap_pipeline(subchunks_file, arxiv_text_dir,
#                                    min_length=8, max_length=20, top_k=5, fuzz_threshold=70)

#     with open(out_path, "w", encoding="utf-8") as f:
#         json.dump(results, f, indent=2, ensure_ascii=False)

#     print("✅ Overlap results saved to:", out_path)
