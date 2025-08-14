import requests

url = "http://127.0.0.1:5000/plagiarism/upload"
file_path = r"C:\Users\infin\Documents\CDAC_TU\ask-my-pdf-chatbot\backend\plagarism\uploads\High_Performance_Optimization_at_the_Door_of_the_Exascale.pdf"

with open(file_path, 'rb') as f:
    files = {'file': f}
    response = requests.post(url, files=files)
    print("Status Code:", response.status_code)
    print("Response:", response.json())