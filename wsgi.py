"""WSGI entrypoint for production servers (gunicorn / waitress).
This exposes the Flask `app` object from app.py.
"""
from app import app  # noqa: F401
