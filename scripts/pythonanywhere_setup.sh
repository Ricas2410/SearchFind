#!/bin/bash
# Script to set up the SearchFind application on PythonAnywhere

echo "=== Setting up SearchFind on PythonAnywhere ==="

# Activate virtual environment
echo "Activating virtual environment..."
source ~/.virtualenvs/searchfind_venv/bin/activate

# Navigate to project directory
echo "Navigating to project directory..."
cd ~/SearchFind

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install django-environ psycopg2-binary

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create sample data
echo "Creating sample companies and job listings..."
python scripts/create_sample_companies_jobs.py

echo "=== Setup complete! ==="
echo "Don't forget to:"
echo "1. Configure your WSGI file"
echo "2. Set up static files in the Web tab"
echo "3. Reload your web app"
