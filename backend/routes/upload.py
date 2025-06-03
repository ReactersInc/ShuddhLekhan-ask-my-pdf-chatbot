from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload", __name__)
UPLOAD_FOLDER = "uploads"

@upload_bp.route('/', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file found"}), 400
    
    file_in = request.files['file']
    if file_in.filename == '':
        return jsonify({"error": "No Selected file"}), 400
    
    filename = secure_filename(file_in.filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file_in.save(save_path)
    
    return jsonify({"message": f"{filename} uploaded successfully", 
                    "filename": filename})
