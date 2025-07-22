from flask import Blueprint, request
from controllers.qa_controller import handle_ask_question

qa_bp = Blueprint("qa", __name__)

@qa_bp.route("/ask", methods=["POST"])
def ask_question():
    return handle_ask_question(request)
