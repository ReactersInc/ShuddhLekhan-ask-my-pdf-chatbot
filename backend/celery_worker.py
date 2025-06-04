from app import create_app
from extensions import celery

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        celery.worker_main()