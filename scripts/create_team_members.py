#!/usr/bin/env python
"""
Script to create team members for the homepage.

This script creates sample team members with profile photos.

Usage:
    python scripts/create_team_members.py
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

from jobs.models import TeamMember

def create_team_members():
    """Create sample team members with profile photos."""
    print("Creating team members...")

    # Sample team member photos
    team_photos = [
        "https://randomuser.me/api/portraits/men/32.jpg",
        "https://randomuser.me/api/portraits/women/28.jpg",
        "https://randomuser.me/api/portraits/men/41.jpg",
        "https://randomuser.me/api/portraits/women/33.jpg",
        "https://randomuser.me/api/portraits/men/52.jpg",
        "https://randomuser.me/api/portraits/women/68.jpg"
    ]

    # Sample team member data
    team_members_data = [
        {
            'name': "Daniel Osei",
            'position': "CEO & Founder",
            'bio': "Daniel founded SearchFind with a vision to transform job searching in Ghana. With over 15 years of experience in HR and recruitment, he understands the challenges faced by both job seekers and employers.",
            'email': "daniel@searchfind.com",
            'linkedin': "https://linkedin.com/in/danielosei",
            'twitter': "https://twitter.com/danielosei",
            'order': 1,
            'photo_url': team_photos[0]
        },
        {
            'name': "Abena Mensah",
            'position': "Chief Technology Officer",
            'bio': "Abena leads our technology team, ensuring that SearchFind's platform is innovative, secure, and user-friendly. She has a background in software engineering and has worked with several tech companies across Africa.",
            'email': "abena@searchfind.com",
            'linkedin': "https://linkedin.com/in/abenamensah",
            'twitter': "https://twitter.com/abenamensah",
            'order': 2,
            'photo_url': team_photos[1]
        },
        {
            'name': "Kwame Boateng",
            'position': "Head of Operations",
            'bio': "Kwame oversees the day-to-day operations of SearchFind, ensuring that our services meet the highest standards. His background in business administration and operations management has been invaluable to our growth.",
            'email': "kwame@searchfind.com",
            'linkedin': "https://linkedin.com/in/kwameboateng",
            'twitter': "https://twitter.com/kwameboateng",
            'order': 3,
            'photo_url': team_photos[2]
        },
        {
            'name': "Ama Darko",
            'position': "Head of Marketing",
            'bio': "Ama leads our marketing efforts, helping to connect job seekers and employers with our platform. Her creative approach and deep understanding of digital marketing have significantly expanded our reach.",
            'email': "ama@searchfind.com",
            'linkedin': "https://linkedin.com/in/amadarko",
            'twitter': "https://twitter.com/amadarko",
            'order': 4,
            'photo_url': team_photos[3]
        },
        {
            'name': "Kofi Adu",
            'position': "Head of Customer Success",
            'bio': "Kofi ensures that all our users have the best possible experience with SearchFind. His team provides support, training, and resources to help job seekers and employers achieve their goals.",
            'email': "kofi@searchfind.com",
            'linkedin': "https://linkedin.com/in/kofiadu",
            'twitter': "https://twitter.com/kofiadu",
            'order': 5,
            'photo_url': team_photos[4]
        },
        {
            'name': "Efua Owusu",
            'position': "Head of HR & Recruitment",
            'bio': "Efua brings her extensive experience in HR and recruitment to help shape SearchFind's services. She understands the needs of both employers and job seekers, ensuring our platform serves them effectively.",
            'email': "efua@searchfind.com",
            'linkedin': "https://linkedin.com/in/efuaowusu",
            'twitter': "https://twitter.com/efuaowusu",
            'order': 6,
            'photo_url': team_photos[5]
        }
    ]

    members_created = 0
    members_updated = 0

    for data in team_members_data:
        # Check if team member already exists
        team_member, created = TeamMember.objects.get_or_create(
            name=data['name'],
            defaults={
                'position': data['position'],
                'bio': data['bio'],
                'email': data['email'],
                'linkedin': data['linkedin'],
                'twitter': data['twitter'],
                'order': data['order'],
                'is_active': True
            }
        )

        if created:
            members_created += 1
            print(f"Created team member: {team_member.name}")
        else:
            # Update existing team member
            team_member.position = data['position']
            team_member.bio = data['bio']
            team_member.email = data['email']
            team_member.linkedin = data['linkedin']
            team_member.twitter = data['twitter']
            team_member.order = data['order']
            team_member.save()
            members_updated += 1
            print(f"Updated team member: {team_member.name}")

        # Download and save photo
        if data['photo_url']:
            try:
                response = requests.get(data['photo_url'])
                if response.status_code == 200:
                    photo_name = f"{data['name'].lower().replace(' ', '_')}.jpg"
                    team_member.photo.save(
                        photo_name,
                        ContentFile(response.content),
                        save=True
                    )
                    print(f"Downloaded photo for {team_member.name}")
                else:
                    print(f"Failed to download photo: HTTP {response.status_code}")
            except Exception as e:
                print(f"Error downloading photo: {str(e)}")

    print(f"Created {members_created} new team members")
    print(f"Updated {members_updated} existing team members")
    print(f"Total: {len(team_members_data)} team members")

if __name__ == "__main__":
    create_team_members()
