from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask
from flask_cors import CORS

from extensions import celery
from routes.upload_routes import upload_bp
from routes.retrieve_summarize import summarize_bp
from routes.qa_routes import qa_bp
from routes.list_routes import list_bp
from routes.qa_routes import qa_bp
from routes.web_summarize import web_bp
from routes.document_route import document_bp
from routes.dashboard_routes import dashboard_bp




def create_app():
    app = Flask(__name__)
    CORS(app)

    # Ensuring required folders exist(otherwise system fails if any of the folder is missing)
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
    

    # Registering Blueprints (similar to Routes in Node.JS)

    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(summarize_bp, url_prefix='/summarize')
    app.register_blueprint(qa_bp, url_prefix="/qa")
    app.register_blueprint(list_bp, url_prefix='/pdfs')
    app.register_blueprint(web_bp) #web summarize
    app.register_blueprint(document_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')



    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
