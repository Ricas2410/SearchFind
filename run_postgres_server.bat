@echo off
call venv\Scripts\activate.bat
set DJANGO_SETTINGS_MODULE=searchfind.settings_prod
python manage.py runserver
