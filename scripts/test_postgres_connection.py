#!/usr/bin/env python
"""
Test PostgreSQL connection using environment variables.

This script:
1. Loads environment variables from .env file
2. Attempts to connect to PostgreSQL using psycopg2
3. Executes a simple query to verify the connection

Usage:
    python scripts/test_postgres_connection.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

def test_connection():
    """Test connection to PostgreSQL database."""
    try:
        import psycopg2
    except ImportError:
        print("Error: psycopg2 is not installed. Please install it with:")
        print("pip install psycopg2-binary")
        return False
    
    # Get connection parameters from environment variables
    db_name = os.environ.get('DB_NAME', 'defaultdb')
    db_user = os.environ.get('DB_USER', 'avnadmin')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_host = os.environ.get('DB_HOST', '')
    db_port = os.environ.get('DB_PORT', '19271')
    
    # Construct connection string
    conn_string = f"dbname='{db_name}' user='{db_user}' password='{db_password}' host='{db_host}' port='{db_port}' sslmode='require'"
    
    print(f"Connecting to PostgreSQL database: {db_host}:{db_port}/{db_name} as {db_user}")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        # Execute a simple query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print("Connection successful!")
        print(f"PostgreSQL version: {version}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print("\nPlease check your connection parameters:")
        print(f"  DB_NAME: {db_name}")
        print(f"  DB_USER: {db_user}")
        print(f"  DB_PASSWORD: {'*' * len(db_password) if db_password else 'Not set'}")
        print(f"  DB_HOST: {db_host}")
        print(f"  DB_PORT: {db_port}")
        
        return False
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("Testing PostgreSQL Connection")
    print("=" * 80)
    
    success = test_connection()
    
    if success:
        print("\nYour PostgreSQL connection is working correctly!")
        print("You can proceed with the migration.")
    else:
        print("\nFailed to connect to PostgreSQL.")
        print("Please check your connection parameters in the .env file.")
        sys.exit(1)
