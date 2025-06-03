import pdfplumber

import pdfplumber

def extract_text_from_pdf(filepath):
    text = ''
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print(f"PDF parsing error: {e}")
        raise e
    return text.strip()
