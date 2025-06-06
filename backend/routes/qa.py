from flask import Blueprint, request, jsonify
from services.qa_service import answer_question_from_pdf

qa_bp = Blueprint("qa", __name__)

@qa_bp.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    pdf_name = data.get("pdf_name")
    question = data.get("question")

    if not pdf_name or not question:
        return jsonify({"error": "pdf_name and question are required"}), 400

    try:
        answer = answer_question_from_pdf(pdf_name, question)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
