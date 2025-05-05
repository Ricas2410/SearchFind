# SearchFind Pre-Deployment Checklist

Use this checklist to ensure your site is ready for deployment.

## Security

- [ ] Generate a new secure SECRET_KEY using `python scripts/generate_secret_key.py`
- [ ] Update the SECRET_KEY in your .env file
- [ ] Set DEBUG=False in your .env file
- [ ] Update ALLOWED_HOSTS with your domain name
- [ ] Verify all sensitive information is stored in environment variables
- [ ] Check for any hardcoded credentials in the codebase
- [ ] Ensure HTTPS is enforced in production

## Database

- [ ] Verify PostgreSQL connection settings
- [ ] Run migrations on the production database
- [ ] Create initial data (categories, plans, etc.)
- [ ] Backup your development database

## Static & Media Files

- [ ] Run `python manage.py collectstatic`
- [ ] Configure AWS S3 for media storage (optional)
- [ ] Verify static files are being served correctly

## Email

- [ ] Verify email settings are correct
- [ ] Test password reset functionality
- [ ] Test notification emails

## SEO & Analytics

- [ ] Verify meta tags are present on all pages
- [ ] Check robots.txt configuration
- [ ] Verify sitemap.xml is generated correctly
- [ ] Add Google Analytics or similar tracking (optional)

## Content

- [ ] Update all placeholder content
- [ ] Verify all legal pages (Terms, Privacy Policy, etc.)
- [ ] Check for broken links
- [ ] Ensure all images have alt text

## Performance

- [ ] Enable caching
- [ ] Optimize database queries
- [ ] Compress static files
- [ ] Test site performance with tools like Lighthouse

## Functionality

- [ ] Test user registration and login
- [ ] Test job posting and application process
- [ ] Test payment processing
- [ ] Test all user flows (job seeker and employer)
- [ ] Verify mobile responsiveness
- [ ] Test on different browsers

## Monitoring & Maintenance

- [ ] Set up error logging with Sentry
- [ ] Configure database backups
- [ ] Set up uptime monitoring
- [ ] Configure scheduled tasks

## Final Steps

- [ ] Run Django's deployment checklist: `python manage.py check --deploy`
- [ ] Verify all tests pass
- [ ] Document any known issues
- [ ] Create deployment documentation
