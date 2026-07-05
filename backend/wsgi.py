"""
Production WSGI entrypoint.
Gunicorn (or any WSGI server) should point here: `gunicorn wsgi:app`
"""
from app import create_app

app = create_app()
