import os
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path, max_pages=50):
    """Extract plain text from PDF using PyMuPDF."""
    doc = fitz.open(pdf_path)
    texts = []
    for page_num, page in enumerate(doc):
        if page_num >= max_pages:
            break
        texts.append(page.get_text("text"))
    return "\n".join(texts)

def chunk_text(text, chunk_size=2000, overlap=200):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
        if start < 0:
            start = 0
    return [c for c in chunks if c]

def load_arxiv_chunks(folder="scraped_data/arxiv/pdfs", chunk_size=2000, overlap=200):
    chunks = []
    pdf_count = 0

    if not os.path.exists(folder):
        return chunks, pdf_count

    for fname in os.listdir(folder):
        if not fname.lower().endswith(".pdf"):
            continue
        pdf_path = os.path.join(folder, fname)
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"[Error] failed to open {fname}: {e}")
            continue

        pdf_count += 1
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()

        # chunk the text
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start += chunk_size - overlap

    return chunks, pdf_count
