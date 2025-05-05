# SearchFind Database Migration Guide

This guide provides step-by-step instructions for migrating your data from SQLite to PostgreSQL.

## Prerequisites

- PostgreSQL database server is set up and accessible
- PostgreSQL credentials are available
- Python and required packages are installed
- Environment variables are configured in `.env` file

## Step 1: Verify Environment Variables

Ensure your `.env` file contains the following PostgreSQL connection details:

```
DB_NAME=defaultdb
DB_USER=avnadmin
DB_PASSWORD=AVNS_XVJ0lm9nrWBSK1OYwSs
DB_HOST=pg-b0522a0-search-searchfind.j.aivencloud.com
DB_PORT=19271
```

## Step 2: Test PostgreSQL Connection

Run the connection test script to verify your PostgreSQL connection:

```bash
python scripts/test_postgres_connection.py
```

If the connection is successful, you'll see a message confirming the connection and displaying the PostgreSQL version.

## Step 3: Backup Your SQLite Database

Before proceeding, create a backup of your SQLite database:

```bash
# Windows
copy db.sqlite3 db.sqlite3.backup

# Linux/Mac
cp db.sqlite3 db.sqlite3.backup
```

## Step 4: Run the Migration Script

Execute the migration script to transfer data from SQLite to PostgreSQL:

```bash
python scripts/migrate_to_postgres_robust.py
```

This script will:
1. Verify database connections
2. Create a backup of your SQLite database
3. Dump data from SQLite to a JSON fixture
4. Apply migrations to PostgreSQL
5. Load data into PostgreSQL
6. Clean up temporary files

## Step 5: Verify the Migration

After the migration completes, verify that your data has been successfully migrated:

1. Update your settings to use PostgreSQL:

```bash
# Set environment variable to use production settings
set DJANGO_SETTINGS_MODULE=searchfind.settings_prod  # Windows
export DJANGO_SETTINGS_MODULE=searchfind.settings_prod  # Linux/Mac
```

2. Run the development server:

```bash
python manage.py runserver
```

3. Browse your site and verify that all data is present and functioning correctly.

## Step 6: Update Your Settings

If everything is working correctly, update your project to use PostgreSQL permanently:

1. Modify your `wsgi.py` file to use production settings (already done)
2. Set the `DJANGO_SETTINGS_MODULE` environment variable in your deployment environment

## Troubleshooting

### Connection Issues

If you encounter connection issues:

1. Verify your PostgreSQL credentials
2. Check if the PostgreSQL server is running and accessible
3. Ensure your firewall allows connections to the PostgreSQL port
4. Verify SSL requirements (sslmode=require)

### Migration Errors

If you encounter errors during migration:

1. Check the error message for specific issues
2. Verify that your SQLite database is not corrupted
3. Ensure you have sufficient permissions to create and modify tables in PostgreSQL
4. Check for any model-specific issues that might require manual intervention

### Data Integrity Issues

If you notice missing or incorrect data after migration:

1. Compare record counts between SQLite and PostgreSQL
2. Check for any unique constraint violations
3. Verify foreign key relationships
4. Consider running specific queries to validate critical data

## Manual Migration (If Needed)

If the automated script fails, you can perform the migration manually:

1. Dump data from SQLite:

```bash
python manage.py dumpdata --exclude contenttypes --exclude auth.permission --exclude sessions > data.json
```

2. Switch to PostgreSQL settings

3. Apply migrations:

```bash
python manage.py migrate
```

4. Load data:

```bash
python manage.py loaddata data.json
```

## Additional Resources

- [Django documentation on migrations](https://docs.djangoproject.com/en/5.2/topics/migrations/)
- [PostgreSQL documentation](https://www.postgresql.org/docs/)
- [psycopg2 documentation](https://www.psycopg.org/docs/)
