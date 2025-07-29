from flask import jsonify
from services.qa_service import answer_question_from_pdf

def handle_ask_question(request):
    try:
        data = request.get_json()
        pdf_name = data.get("pdf_name")
        question = data.get("question")

        print('pdf name' , pdf_name)
        print('question' , question)


        if not pdf_name or not question:
            return jsonify({"error": "pdf_name and question are required"}), 400

        answer = answer_question_from_pdf(pdf_name, question)
        return jsonify({"answer": answer})
        
    except Exception as e:
        print('Faillllllllll')
        return jsonify({"error": str(e)}), 500
