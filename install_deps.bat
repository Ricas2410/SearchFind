@echo off
call venv\Scripts\activate.bat
pip install sentry-sdk django-compressor psycopg2-binary
echo Dependencies installed successfully!
