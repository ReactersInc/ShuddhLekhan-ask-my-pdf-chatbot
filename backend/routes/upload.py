from flask import Blueprint , request , jsonify
import os
from werkzeug.utils import secure_filename

from services.parse_pdf import extract_text_from_pdf
from services.summarize import generate_summary, save_summary

upload_bp = Blueprint("upload" , __name__)
UPLOAD_FOLDER = "uploads"

@upload_bp.route('/', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error" : "No file found"}),400
    
    file_in = request.files['file']
    if file_in.filename == '':
        return jsonify({"error": "No Selected file"}),400
    
    filename = secure_filename(file_in.filename)
    base_filename = os.path.splitext(filename)[0]

    save_path = os.path.join(UPLOAD_FOLDER , filename)
    os.makedirs(UPLOAD_FOLDER , exist_ok=True)
    file_in.save(save_path)
    
    try:
        #Parsing and Summarizing
        text = extract_text_from_pdf(save_path)
        summary = generate_summary(text)
        save_summary(summary ,base_filename)
    
    except Exception as e:
        return jsonify({"error": str(e)}) , 500


    return jsonify({"message": f"{filename} uploaded successfully", 
                    "filename": filename})