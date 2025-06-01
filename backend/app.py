from flask import Flask
from routes.upload import upload_bp
from routes.summarize import summarize_bp
from routes.qa import qa_bp
from routes.pdf_list import list_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)       #enables CORS for React Frontend

# Registering Blueprints (Similar to Rotues in Node.JS)

app.register_blueprint(upload_bp , url_prefix='/upload')
app.register_blueprint(summarize_bp , url_prefix='/summarize')
app.register_blueprint(qa_bp, url_prefix="/ask")
app.register_blueprint(list_bp, url_prefix="/pdfs")


if __name__ == "__main__":
    app.run(debug=True)