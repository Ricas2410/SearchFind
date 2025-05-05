# SearchFind Job Board

A comprehensive job board platform connecting employers with job seekers.

## Features

- Job posting and management for employers
- Job search and application for job seekers
- User profiles and resume management
- Application tracking system
- Messaging between employers and applicants
- Notifications system
- Newsletter subscription
- Admin dashboard for site management

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your environment variables (see `.env.example`)
6. Run migrations: `python manage.py migrate`
7. Create a superuser: `python scripts/create_superuser.py`
8. Run the development server: `python manage.py runserver`

## Production Deployment

For detailed instructions on deploying to PythonAnywhere, see the [Deployment Guide](DEPLOYMENT_GUIDE.md).

### Quick Deployment

1. Set up your PythonAnywhere account
2. Clone the repository
3. Set up a virtual environment and install dependencies
4. Configure environment variables in `.env`
5. Run the setup script: `python scripts/setup_pythonanywhere.py yourdomain.com`
6. Configure the web app in the PythonAnywhere dashboard

### Deployment Scripts

The project includes several scripts to help with deployment and maintenance:

- `scripts/setup_pythonanywhere.py`: Initial setup for PythonAnywhere
- `scripts/deploy.py`: Deploy updates to the application
- `scripts/backup_database.py`: Backup the database
- `scripts/restore_database.py`: Restore the database from a backup
- `scripts/update_site_domain.py`: Update the site domain
- `scripts/check_settings.py`: Check the application settings
- `scripts/create_superuser.py`: Create a superuser account

## Scheduled Tasks

### Expiring Jobs

The system includes a management command to automatically mark jobs with passed application deadlines as expired:

```
python manage.py expire_jobs
```

To run this command automatically:

#### On Unix/Linux (using cron)

Add a cron job to run daily:

```
# Edit crontab
crontab -e

# Add this line to run daily at midnight
0 0 * * * cd /path/to/project && /path/to/venv/bin/python manage.py expire_jobs
```

#### On Windows (using Task Scheduler)

1. Create a batch file (e.g., `expire_jobs.bat`) with:
```
@echo off
cd C:\path\to\project
call venv\Scripts\activate
python manage.py expire_jobs
```

2. Open Task Scheduler and create a new task:
   - Trigger: Daily at midnight
   - Action: Start a program
   - Program/script: `C:\path\to\project\expire_jobs.bat`

### Sending Expiration Warnings

The system includes a management command to send email notifications to employers about jobs that are about to expire:

```
python manage.py send_expiration_warnings --days=3
```

This will send warnings for jobs that will expire within the next 3 days. You can adjust the number of days as needed.

To run this command automatically:

#### On Unix/Linux (using cron)

Add a cron job to run daily:

```
# Edit crontab
crontab -e

# Add this line to run daily at 8 AM
0 8 * * * cd /path/to/project && /path/to/venv/bin/python manage.py send_expiration_warnings --days=3
```

#### On Windows (using Task Scheduler)

1. Create a batch file (e.g., `send_warnings.bat`) with:
```
@echo off
cd C:\path\to\project
call venv\Scripts\activate
python manage.py send_expiration_warnings --days=3
```

2. Open Task Scheduler and create a new task:
   - Trigger: Daily at 8 AM
   - Action: Start a program
   - Program/script: `C:\path\to\project\send_warnings.bat`

## License

[MIT License](LICENSE)
