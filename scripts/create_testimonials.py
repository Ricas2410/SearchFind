#!/usr/bin/env python
"""
Script to create testimonials for the homepage.

This script creates sample testimonials with profile images.

Usage:
    python scripts/create_testimonials.py
"""

import os
import sys
import requests
from pathlib import Path
from django.core.files.base import ContentFile

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from jobs.models import Testimonial

User = get_user_model()

def create_testimonials():
    """Create sample testimonials with profile images."""
    print("Creating testimonials...")

    # Get admin user
    try:
        admin = User.objects.get(email='admin@searchfind.com')
        print(f"Using admin user: {admin.email}")
    except User.DoesNotExist:
        print("Admin user not found. Please create an admin user first.")
        return

    # Sample profile image URLs
    profile_images = [
        "https://randomuser.me/api/portraits/men/75.jpg",
        "https://randomuser.me/api/portraits/women/65.jpg",
        "https://randomuser.me/api/portraits/men/32.jpg",
        "https://randomuser.me/api/portraits/women/44.jpg",
        "https://randomuser.me/api/portraits/men/55.jpg"
    ]

    # Sample testimonial data
    testimonials_data = [
        {
            'name': "John Mensah",
            'content': "I found my dream job through SearchFind! The platform is intuitive and made my job search so much easier. Highly recommended for all job seekers in Ghana.",
            'rating': 5,
            'user_role': "Software Developer",
            'image_url': profile_images[0]
        },
        {
            'name': "Akosua Boateng",
            'content': "As an employer, SearchFind has helped us find qualified candidates quickly. The filtering options are excellent and save us a lot of time in the recruitment process.",
            'rating': 5,
            'user_role': "HR Manager",
            'image_url': profile_images[1]
        },
        {
            'name': "Kwame Osei",
            'content': "The job alerts feature is fantastic! I received notifications for positions that matched my skills perfectly, and I'm now working at a great company thanks to SearchFind.",
            'rating': 4,
            'user_role': "Marketing Specialist",
            'image_url': profile_images[2]
        },
        {
            'name': "Abena Poku",
            'content': "SearchFind's resume builder helped me create a professional CV that stood out to employers. Within weeks, I had multiple interview offers.",
            'rating': 5,
            'user_role': "Accountant",
            'image_url': profile_images[3]
        },
        {
            'name': "Kofi Adu",
            'content': "The career resources and advice on SearchFind are invaluable. I learned how to improve my interview skills and negotiate a better salary package.",
            'rating': 4,
            'user_role': "Project Manager",
            'image_url': profile_images[4]
        }
    ]

    testimonials_created = 0
    testimonials_updated = 0

    for data in testimonials_data:
        # Create a user for this testimonial if needed
        user_email = f"{data['name'].lower().replace(' ', '.')}@example.com"
        username = user_email.split('@')[0]

        # Check if user exists
        try:
            user = User.objects.get(email=user_email)
            user_created = False
            print(f"Using existing user: {user.email}")
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create(
                email=user_email,
                username=username,  # Set username explicitly
                first_name=data['name'].split()[0],
                last_name=data['name'].split()[1] if len(data['name'].split()) > 1 else '',
                is_active=True,
                user_type='job_seeker'
            )
            user_created = True
            print(f"Created user: {user.email}")

        if user_created:
            user.set_password('password123')
            user.save()
            print(f"Created user: {user.email}")

        # Create testimonial
        testimonial, created = Testimonial.objects.get_or_create(
            user=user,
            defaults={
                'content': data['content'],
                'rating': data['rating'],
                'user_role': data['user_role'],
                'is_active': True
            }
        )

        if created:
            testimonials_created += 1
            print(f"Created testimonial from {user.get_full_name()}")
        else:
            # Update existing testimonial
            testimonial.content = data['content']
            testimonial.rating = data['rating']
            testimonial.user_role = data['user_role']
            testimonial.save()
            testimonials_updated += 1
            print(f"Updated testimonial from {user.get_full_name()}")

        # Download and save profile image
        if data['image_url']:
            try:
                response = requests.get(data['image_url'])
                if response.status_code == 200:
                    image_name = f"{user.email.split('@')[0]}_profile.jpg"
                    testimonial.profile_image.save(
                        image_name,
                        ContentFile(response.content),
                        save=True
                    )
                    print(f"Downloaded profile image for {user.get_full_name()}")
                else:
                    print(f"Failed to download profile image: HTTP {response.status_code}")
            except Exception as e:
                print(f"Error downloading profile image: {str(e)}")

    print(f"Created {testimonials_created} new testimonials")
    print(f"Updated {testimonials_updated} existing testimonials")
    print(f"Total: {len(testimonials_data)} testimonials")

if __name__ == "__main__":
    create_testimonials()
