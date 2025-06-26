import os 

UPLOAD_FOLDER = 'uploads'
SUMMARY_FOLDER = 'summaries'

def get_all_pdf_with_summaries():
    pdfs = []

    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith(".pdf"):
            pdf_name = os.path.splitext(filename)[0]
            summary_file_path = os.path.join(SUMMARY_FOLDER, f"{pdf_name}.txt")

            summary = "summary not available"
            if os.path.exists(summary_file_path):
                with open(summary_file_path, "r") as f:
                    summary = f.read

            pdfs.append({
                "filename" : filename,
                "summary" : summary
            })

    return pdfs