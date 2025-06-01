import pdfplumber

def extract_text_from_pdf(filepath):
    
    text =''
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = text + page.extract_text() or ''
    
    return text.strip()