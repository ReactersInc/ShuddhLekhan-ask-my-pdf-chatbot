import fitz 

def extract_text_from_pdf(filepath):
    try:
        doc = fitz.open(filepath)
        text = "\n".join([page.get_text() for page in doc])
        return text.strip()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""
