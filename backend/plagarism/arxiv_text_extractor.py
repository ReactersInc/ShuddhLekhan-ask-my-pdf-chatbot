# arxiv_text_extractor.py
import os
from pathlib import Path
import fitz  
import re

# ===============================
# STEP 1: Text Cleaning Helpers
# ===============================
def remove_references(text):
    """
    Remove references/bibliography section from paper text.
    """
    ref_pattern = re.compile(r'\b(references|bibliography|citations)\b', re.IGNORECASE)
    match = ref_pattern.search(text)
    if match:
        return text[:match.start()]
    return text

def clean_inline_citations(text):
    """
    Remove inline citations like [12], [3,5], (Smith, 2020), (Smith et al., 2020).
    """
    # Remove numeric bracket citations: [12], [3,5], [1–4]
    text = re.sub(r'\[\s*\d+(?:\s*[-,]\s*\d+)*\s*\]', '', text)

    # Remove author-year citations: (Smith, 2020), (Smith et al., 2020)
    text = re.sub(r'\([A-Z][A-Za-z]+(?:\s+et al\.)?,\s*\d{4}\)', '', text)

    # Remove multiple citations in one parenthesis: (Smith, 2020; Johnson, 2019)
    text = re.sub(r'\((?:[A-Z][A-Za-z]+(?:\s+et al\.)?,\s*\d{4};?\s*)+\)', '', text)

    return text

# ===============================
# STEP 2: Extract text from PDFs
# ===============================
def extract_text_from_pdf(pdf_path):
    text = []
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                content = page.get_text("text")
                if content:
                    text.append(content)
    except Exception as e:
        print(f"❌ Error extracting {pdf_path}: {e}")
    return "\n".join(text)

def build_arxiv_texts(arxiv_pdf_dir="scraped_data/arxiv/pdfs",
                      out_dir="scraped_data/arxiv/texts"):
    os.makedirs(out_dir, exist_ok=True)
    results = {}
    for pdf_file in os.listdir(arxiv_pdf_dir):
        if pdf_file.lower().endswith(".pdf"):
            pdf_path = os.path.join(arxiv_pdf_dir, pdf_file)
            text = extract_text_from_pdf(pdf_path)

            # Clean text before saving
            text = remove_references(text)
            text = clean_inline_citations(text)

            base_name = Path(pdf_file).stem
            txt_path = os.path.join(out_dir, base_name + ".txt")

            if os.path.exists(txt_path) and os.path.getsize(txt_path) > 0:
                print(f"⏩ Skipping {pdf_file}, text already extracted.")
                results[base_name] = txt_path
                continue

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            results[base_name] = txt_path
            print(f"✅ Saved text for {pdf_file} → {txt_path}")
    return results


if __name__ == "__main__":
    # Example run: just extract and clean text
    build_arxiv_texts()
