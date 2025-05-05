# SearchFind Deployment Guide for PythonAnywhere

This guide provides step-by-step instructions for deploying the SearchFind application on PythonAnywhere.

## Prerequisites

- A PythonAnywhere account (www.pythonanywhere.com)
- PostgreSQL database credentials (provided in the .env file)
- Git repository with the SearchFind code

## Deployment Steps

### 1. Set Up PythonAnywhere Account

1. Log in to your PythonAnywhere account at https://www.pythonanywhere.com/
2. Go to the Dashboard

### 2. Clone the Repository

1. Open a Bash console from the PythonAnywhere dashboard
2. Clone the repository:
   ```bash
   cd ~
   git clone https://github.com/yourusername/SearchFind.git
   cd SearchFind
   ```

### 3. Set Up Virtual Environment

1. Create a virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 searchfind_venv
   ```

2. Activate the virtual environment:
   ```bash
   workon searchfind_venv
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 4. Configure Environment Variables

1. Create the .env file:
   ```bash
   nano .env
   ```

2. Add the following content (replace with your actual values):
   ```
   # Django settings
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=searchfind.pythonanywhere.com,www.searchfind.pythonanywhere.com

   # Database settings
   DATABASE_URL=postgres://avnadmin:AVNS_THGWpg2byHA3Pt9rtW6@searchfind-seachfind.d.aivencloud.com:16296/defaultdb?sslmode=require

   # Email settings
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=skillnetservices@gmail.com
   EMAIL_HOST_PASSWORD=your-email-password
   EMAIL_USE_TLS=True
   DEFAULT_FROM_EMAIL=skillnetservices@gmail.com

   # Site settings
   SITE_URL=https://searchfind.pythonanywhere.com
   ```

### 5. Set Up the Database and Initial Configuration

You can use the setup script to automate most of the setup process:

```bash
python scripts/setup_pythonanywhere.py searchfind.pythonanywhere.com
```

This script will:
- Create necessary directories
- Run migrations
- Create a superuser
- Collect static files
- Update the site domain
- Check settings

Alternatively, you can run each step manually:

1. Run migrations:
   ```bash
   python manage.py migrate
   ```

2. Create a superuser:
   ```bash
   python scripts/create_superuser.py
   ```

3. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

4. Update the site domain:
   ```bash
   python scripts/update_site_domain.py searchfind.pythonanywhere.com
   ```

5. Check settings:
   ```bash
   python scripts/check_settings.py
   ```

### 7. Configure Web App on PythonAnywhere

1. Go to the Web tab in the PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.10
5. Enter the path to your project: `/home/searchfind/SearchFind`

### 8. Configure WSGI File

1. Click on the WSGI configuration file link in the Web tab
2. Replace the content with the content from `searchfind_pythonanywhere_wsgi.py`
3. Save the file

### 9. Configure Static Files

1. In the Web tab, scroll down to "Static files"
2. Add the following mappings:
   - URL: `/static/` -> Directory: `/home/searchfind/SearchFind/staticfiles`
   - URL: `/media/` -> Directory: `/home/searchfind/SearchFind/media`

### 10. Configure Virtual Environment

1. In the Web tab, scroll to "Virtualenv"
2. Enter the path to your virtual environment: `/home/searchfind/.virtualenvs/searchfind_venv`

### 11. Update Site in Django Admin

1. Reload your web app
2. Go to your site's admin panel: `https://searchfind.pythonanywhere.com/admin/`
3. Navigate to Sites under the SITES section
4. Edit the existing site (ID: 1) and update:
   - Domain name: `searchfind.pythonanywhere.com` (without http/https)
   - Display name: `SearchFind`

### 12. Final Steps

1. Reload your web app from the PythonAnywhere Web tab
2. Visit your site at `https://searchfind.pythonanywhere.com`

## Troubleshooting

### Error Logs

If you encounter issues, check the error logs in the PythonAnywhere Web tab:
- Error log
- Server log
- Access log

### Common Issues

1. **Database Connection Issues**:
   - Verify your DATABASE_URL is correct
   - Check if your IP is whitelisted in the database provider

2. **Static Files Not Loading**:
   - Ensure you've run `collectstatic`
   - Verify the static files mappings in the Web tab

3. **WSGI Configuration Issues**:
   - Double-check the path to your project
   - Ensure the DJANGO_SETTINGS_MODULE is set correctly

## Maintenance

### Updating the Application

You can use the deploy script to automate the update process:

```bash
python scripts/deploy.py searchfind.pythonanywhere.com
```

This script will:
- Backup the database
- Run migrations
- Collect static files
- Update the site domain
- Check settings

Alternatively, you can run each step manually:

1. Pull the latest changes:
   ```bash
   cd ~/SearchFind
   git pull
   ```

2. Install any new dependencies:
   ```bash
   workon searchfind_venv
   pip install -r requirements.txt
   ```

3. Backup the database:
   ```bash
   python scripts/backup_database.py
   ```

4. Run migrations if needed:
   ```bash
   python manage.py migrate
   ```

5. Collect static files if needed:
   ```bash
   python manage.py collectstatic --noinput
   ```

6. Update the site domain if needed:
   ```bash
   python scripts/update_site_domain.py searchfind.pythonanywhere.com
   ```

7. Reload the web app from the PythonAnywhere Web tab

### Database Backup and Restore

#### Backup

You can backup the database using the backup script:

```bash
python scripts/backup_database.py [output_dir]
```

This will create a JSON dump of the database in the specified directory (or `backups` by default).

#### Restore

You can restore the database from a backup using the restore script:

```bash
python scripts/restore_database.py backups/db_backup_20250505_010000.json
```

This will load the JSON dump into the database.

## Security Considerations

1. Keep DEBUG=False in production
2. Regularly update dependencies
3. Use HTTPS for all connections
4. Protect sensitive information in .env file
5. Regularly rotate passwords and API keys
