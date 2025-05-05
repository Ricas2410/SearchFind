import os
import django
from django.db import connection

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')
django.setup()

# Fix the migration issue
with connection.cursor() as cursor:
    # Check if sites migrations are in the database
    cursor.execute("SELECT * FROM django_migrations WHERE app = 'sites'")
    sites_migrations = cursor.fetchall()
    
    if not sites_migrations:
        print("Adding sites migrations to the database...")
        # Add sites migrations to the database
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, datetime('now'))",
            ['sites', '0001_initial']
        )
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, datetime('now'))",
            ['sites', '0002_alter_domain_unique']
        )
        print("Sites migrations added successfully.")
    else:
        print("Sites migrations already exist in the database.")
    
    # Create the django_site table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS django_site (
        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        domain varchar(100) NOT NULL,
        name varchar(50) NOT NULL
    )
    """)
    
    # Check if the default site exists
    cursor.execute("SELECT * FROM django_site WHERE id = 1")
    default_site = cursor.fetchone()
    
    if not default_site:
        print("Creating default site...")
        cursor.execute(
            "INSERT INTO django_site (id, domain, name) VALUES (%s, %s, %s)",
            [1, '127.0.0.1:8000', 'SearchFind']
        )
        print("Default site created successfully.")
    else:
        print("Default site already exists.")

print("Migration fix completed successfully.")
