# SearchFind Deployment Guide

This guide provides instructions for deploying the SearchFind job board application to a production environment.

## Prerequisites

- Python 3.13.1 or higher
- Git
- A production server (Heroku, DigitalOcean, AWS, etc.)
- SMTP email service (Gmail, SendGrid, etc.)

## Deployment Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd searchfind
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root directory based on the `.env.example` file:

```bash
cp .env.example .env
```

Edit the `.env` file and set the following variables:

- `SECRET_KEY`: A secure random string
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `EMAIL_HOST`: SMTP server host
- `EMAIL_PORT`: SMTP server port
- `EMAIL_HOST_USER`: SMTP username
- `EMAIL_HOST_PASSWORD`: SMTP password
- `DEFAULT_FROM_EMAIL`: Default sender email
- `SITE_URL`: Your site's URL (e.g., https://yourdomain.com)

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Collect Static Files

```bash
python manage.py collectstatic --no-input
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

### 7. Set Up Scheduled Tasks

#### Expiring Jobs

Set up a cron job to automatically mark jobs with passed application deadlines as expired:

```bash
# Run daily at midnight
0 0 * * * cd /path/to/project && /path/to/venv/bin/python manage.py expire_jobs
```

#### Sending Expiration Warnings

Set up a cron job to send email notifications to employers about jobs that are about to expire:

```bash
# Run daily at 8 AM
0 8 * * * cd /path/to/project && /path/to/venv/bin/python manage.py send_expiration_warnings --days=3
```

## Deployment Options

### Option 1: Heroku

1. Install the Heroku CLI and log in:

```bash
heroku login
```

2. Create a new Heroku app:

```bash
heroku create your-app-name
```

3. Set environment variables:

```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
heroku config:set EMAIL_HOST=smtp.gmail.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_HOST_USER=your-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=your-app-password
heroku config:set EMAIL_USE_TLS=True
heroku config:set DEFAULT_FROM_EMAIL=your-email@gmail.com
heroku config:set SITE_URL=https://your-app-name.herokuapp.com
```

4. Deploy to Heroku:

```bash
git push heroku main
```

5. Set up Heroku Scheduler for scheduled tasks:

- Go to your Heroku dashboard
- Add the "Heroku Scheduler" add-on
- Add the following tasks:
  - `python manage.py expire_jobs` (daily)
  - `python manage.py send_expiration_warnings --days=3` (daily)

### Option 2: DigitalOcean

1. Create a Droplet on DigitalOcean
2. Set up a Django project using the Django deployment guide
3. Clone your repository to the server
4. Set up environment variables in the `.env` file
5. Install dependencies and run migrations
6. Set up Nginx and Gunicorn
7. Set up SSL with Let's Encrypt
8. Set up cron jobs for scheduled tasks

## Post-Deployment Tasks

1. Test the application thoroughly
2. Set up initial data (categories, plans, etc.)
3. Configure payment integration
4. Set up monitoring and error tracking
5. Set up backups

## Troubleshooting

- Check the logs for errors: `heroku logs --tail` (for Heroku)
- Verify environment variables are set correctly
- Ensure database migrations have been applied
- Check that static files are being served correctly
- Verify email settings are correct by testing the password reset functionality
