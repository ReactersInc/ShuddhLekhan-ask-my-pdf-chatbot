from flask import Blueprint, request, jsonify
from services.qa_service import get_qa_answer

qa_bp = Blueprint("qa", __name__)

@qa_bp.route("/ask", methods=["POST"])
def ask_question():
    data = request.json
    pdf = data.get("pdf")  # no .pdf extension
    question = data.get("question")

    if not pdf or not question:
        return jsonify({"error": "PDF and question required"}), 400
    
    try:
        answer = get_qa_answer(pdf, question)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
