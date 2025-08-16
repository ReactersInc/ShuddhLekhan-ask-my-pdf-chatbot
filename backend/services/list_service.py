import os 

UPLOAD_FOLDER = 'uploads'
SUMMARY_FOLDER = 'summaries'

def get_all_pdf_with_summaries():
    pdfs = []

    # Walk through all uploaded files recursively
    for root, _, files in os.walk(UPLOAD_FOLDER):
        for filename in files:
            if filename.endswith(".pdf"):
                # Get relative path from uploads folder
                abs_path = os.path.join(root, filename)
                relative_path = os.path.relpath(abs_path, start=UPLOAD_FOLDER)
                
                pdf_name = os.path.splitext(filename)[0]
                
                # Construct corresponding summary path
                summary_rel_path = os.path.splitext(relative_path)[0] + ".txt"
                summary_file_path = os.path.join(SUMMARY_FOLDER, summary_rel_path)

                summary = "summary not available"
                if os.path.exists(summary_file_path):
                    try:
                        # Try multiple encodings to handle different file formats
                        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
                        for encoding in encodings:
                            try:
                                with open(summary_file_path, "r", encoding=encoding) as f:
                                    summary = f.read()
                                break  # Success, exit the encoding loop
                            except UnicodeDecodeError:
                                continue  # Try next encoding
                        else:
                            # If all encodings fail, read as binary and decode with errors='ignore'
                            with open(summary_file_path, "rb") as f:
                                summary = f.read().decode('utf-8', errors='ignore')
                    except Exception as e:
                        summary = f"Error reading summary: {str(e)}"

                pdfs.append({
                    "filename": relative_path,
                    "summary": summary
                })

    return pdfs