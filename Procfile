web: python manage.py db upgrade; gunicorn web_runner:app
worker: celery worker -A web_runner.celery --loglevel=info