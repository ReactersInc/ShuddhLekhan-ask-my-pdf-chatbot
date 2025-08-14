# test_qa.py
from services.qa_service import answer_question_from_pdf

PDF_NAME = "Summarizing_Charts_and_Graphs_with_Context"

def run_test(question: str):
    print(f"\n---\nQuestion: {question}")
    try:
        answer = answer_question_from_pdf(PDF_NAME, question, top_k=5)
        print("Answer:\n", answer)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    # 1) Table‑focused
    # run_test("Describe the table 1 in brief")

    # 2) Image‑focused
    run_test("Describe the image p5_2.png in brief.")

