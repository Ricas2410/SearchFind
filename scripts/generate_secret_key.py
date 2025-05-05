#!/usr/bin/env python
"""
Generate a secure Django secret key.
"""
import secrets
import string

def generate_secret_key(length=50):
    """Generate a secure random string for use as a Django secret key."""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(length))

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("\nGenerated Django Secret Key:")
    print("-" * 60)
    print(secret_key)
    print("-" * 60)
    print("\nAdd this to your .env file as:")
    print("SECRET_KEY=" + secret_key)
    print("\n")
