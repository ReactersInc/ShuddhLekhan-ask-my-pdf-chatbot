import os
import fitz  # PyMuPDF
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
