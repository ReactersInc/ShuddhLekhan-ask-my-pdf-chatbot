import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from extensions import celery
from routes.upload import upload_bp
from routes.summarize import summarize_bp
from routes.qa import qa_bp
from routes.pdf_list import list_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Ensure required folders exist
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("summaries", exist_ok=True)

    # Celery config
    app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # Update Celery config after app config
    celery.conf.update(app.config)

    # Required to run Celery tasks with Flask app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

    # Register Blueprints
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(summarize_bp, url_prefix='/summarize')
    app.register_blueprint(qa_bp, url_prefix='/ask')
    app.register_blueprint(list_bp, url_prefix='/pdfs')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
