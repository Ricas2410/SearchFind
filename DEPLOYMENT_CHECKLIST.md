# SearchFind Deployment Checklist

Use this checklist to ensure a smooth deployment of the SearchFind application to PythonAnywhere.

## Pre-Deployment Checks

- [ ] All code changes are committed and pushed to the repository
- [ ] Database migrations are up to date
- [ ] Static files are collected
- [ ] Environment variables are configured
- [ ] Debug mode is disabled
- [ ] ALLOWED_HOSTS is properly configured
- [ ] Email settings are configured
- [ ] Database connection is working

## Deployment Steps

### 1. Set Up PythonAnywhere Account

- [ ] Create a PythonAnywhere account (if not already done)
- [ ] Log in to PythonAnywhere

### 2. Clone the Repository

- [ ] Open a Bash console
- [ ] Clone the repository:
  ```bash
  cd ~
  git clone https://github.com/yourusername/SearchFind.git
  cd SearchFind
  ```

### 3. Set Up Virtual Environment

- [ ] Create a virtual environment:
  ```bash
  mkvirtualenv --python=/usr/bin/python3.10 searchfind_venv
  ```
- [ ] Activate the virtual environment:
  ```bash
  workon searchfind_venv
  ```
- [ ] Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 4. Configure Environment Variables

- [ ] Create the .env file:
  ```bash
  nano .env
  ```
- [ ] Add environment variables (see DEPLOYMENT_GUIDE.md for details)

### 5. Set Up the Database

- [ ] Run migrations:
  ```bash
  python manage.py migrate
  ```
- [ ] Create a superuser:
  ```bash
  python scripts/create_superuser.py
  ```

### 6. Collect Static Files

- [ ] Collect static files:
  ```bash
  python manage.py collectstatic --noinput
  ```

### 7. Configure Web App on PythonAnywhere

- [ ] Go to the Web tab
- [ ] Add a new web app
- [ ] Choose "Manual configuration"
- [ ] Select Python 3.10
- [ ] Enter the path to your project

### 8. Configure WSGI File

- [ ] Click on the WSGI configuration file link
- [ ] Replace the content with the content from `pythonanywhere_wsgi.py`
- [ ] Save the file

### 9. Configure Static Files

- [ ] In the Web tab, scroll down to "Static files"
- [ ] Add the following mappings:
  - URL: `/static/` -> Directory: `/home/searchfind/SearchFind/staticfiles`
  - URL: `/media/` -> Directory: `/home/searchfind/SearchFind/media`

### 10. Configure Virtual Environment

- [ ] In the Web tab, scroll to "Virtualenv"
- [ ] Enter the path to your virtual environment

### 11. Update Site in Django Admin

- [ ] Reload your web app
- [ ] Go to your site's admin panel
- [ ] Navigate to Sites under the SITES section
- [ ] Edit the existing site (ID: 1) and update:
  - Domain name: `searchfind.pythonanywhere.com`
  - Display name: `SearchFind`

### 12. Final Steps

- [ ] Reload your web app
- [ ] Visit your site to verify it's working

## Post-Deployment Checks

- [ ] Site loads correctly
- [ ] Static files are served correctly
- [ ] User registration works
- [ ] User login works
- [ ] Job listings are displayed
- [ ] Job search works
- [ ] Job application works
- [ ] Admin dashboard works
- [ ] Email notifications work

## Troubleshooting

If you encounter issues, check:

- [ ] Error logs in the PythonAnywhere Web tab
- [ ] Database connection
- [ ] WSGI configuration
- [ ] Static files configuration
- [ ] Environment variables

## Notes

- Remember to update the site domain using the `update_site_domain.py` script:
  ```bash
  python scripts/update_site_domain.py searchfind.pythonanywhere.com
  ```
- Verify settings using the `check_settings.py` script:
  ```bash
  python scripts/check_settings.py
  ```
