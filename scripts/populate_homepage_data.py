import os
import sys
import django
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.contrib.auth import get_user_model

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchfind.settings')
django.setup()

from jobs.models import Testimonial, TeamMember, TrustedCompany

User = get_user_model()

def create_testimonials():
    """Create sample testimonials with profile images."""
    print("Creating testimonials...")

    # Get some users or create them if needed
    users = User.objects.filter(is_active=True)[:5]
    if not users:
        print("No users found. Please create some users first.")
        return

    # Sample profile image URLs (using placeholder images)
    profile_images = [
        "https://randomuser.me/api/portraits/men/75.jpg",
        "https://randomuser.me/api/portraits/women/65.jpg",
        "https://randomuser.me/api/portraits/men/32.jpg",
        "https://randomuser.me/api/portraits/women/44.jpg",
        "https://randomuser.me/api/portraits/men/55.jpg"
    ]

    testimonials_data = [
        {
            'user': users[0],
            'content': "SearchFind made my job search incredibly easy. I found my dream position within weeks of signing up. The platform is intuitive and the job matches were spot on!",
            'rating': 5,
            'user_role': "Software Developer",
            'image_url': profile_images[0]
        },
        {
            'user': users[1],
            'content': "As an employer, I've been able to find qualified candidates quickly. The platform's filtering options help us narrow down applicants to find the perfect fit for our team.",
            'rating': 5,
            'user_role': "HR Manager",
            'image_url': profile_images[1]
        },
        {
            'user': users[2],
            'content': "The application tracking system is a game-changer. I can easily see the status of all my applications and communicate directly with employers.",
            'rating': 4,
            'user_role': "UX Designer",
            'image_url': profile_images[2]
        },
        {
            'user': users[3],
            'content': "We've hired three team members through SearchFind in the past year. The quality of candidates is consistently high, and the platform is easy to use.",
            'rating': 5,
            'user_role': "CTO",
            'image_url': profile_images[3]
        },
        {
            'user': users[4],
            'content': "The privacy controls are excellent. I appreciate being able to control who sees my profile and resume. It's made my job search much more comfortable.",
            'rating': 4,
            'user_role': "Marketing Specialist",
            'image_url': profile_images[4]
        }
    ]

    for data in testimonials_data:
        # Create testimonial
        testimonial, created = Testimonial.objects.get_or_create(
            user=data['user'],
            content=data['content'],
            defaults={
                'rating': data['rating'],
                'user_role': data['user_role'],
                'is_active': True
            }
        )

        # Download and save profile image to user's profile
        if data['image_url'] and hasattr(data['user'], 'profile_picture'):
            try:
                response = requests.get(data['image_url'])
                if response.status_code == 200:
                    image_name = f"profile_{data['user'].username}.jpg"
                    data['user'].profile_picture.save(
                        image_name,
                        ContentFile(response.content),
                        save=True
                    )
                    print(f"Downloaded profile image for {data['user'].get_full_name()}")
                else:
                    print(f"Failed to download profile image for {data['user'].get_full_name()}: HTTP {response.status_code}")
            except Exception as e:
                print(f"Error downloading profile image for {data['user'].get_full_name()}: {str(e)}")

    print(f"Created {len(testimonials_data)} testimonials")

def create_team_members():
    """Create sample team members with actual profile images."""
    print("Creating team members...")

    # Sample profile image URLs (using placeholder images)
    profile_images = [
        "https://randomuser.me/api/portraits/women/32.jpg",  # Sarah
        "https://randomuser.me/api/portraits/men/45.jpg",    # Michael
        "https://randomuser.me/api/portraits/women/68.jpg",  # Emily
        "https://randomuser.me/api/portraits/men/22.jpg"     # David
    ]

    team_members_data = [
        {
            'name': "Sarah Johnson",
            'position': "CEO & Founder",
            'bio': "With over 15 years of experience in HR and recruitment, Sarah leads our mission to connect talent with opportunity.",
            'email': "sarah@searchfind.com",
            'linkedin': "https://linkedin.com/in/sarahjohnson",
            'twitter': "https://twitter.com/sarahjohnson",
            'order': 1,
            'image_url': profile_images[0]
        },
        {
            'name': "Michael Chen",
            'position': "CTO",
            'bio': "Michael oversees our technical infrastructure, ensuring a seamless experience for job seekers and employers alike.",
            'email': "michael@searchfind.com",
            'linkedin': "https://linkedin.com/in/michaelchen",
            'twitter': "https://twitter.com/michaelchen",
            'order': 2,
            'image_url': profile_images[1]
        },
        {
            'name': "Emily Rodriguez",
            'position': "Head of Marketing",
            'bio': "Emily drives our marketing strategy, helping connect employers with the perfect candidates for their teams.",
            'email': "emily@searchfind.com",
            'linkedin': "https://linkedin.com/in/emilyrodriguez",
            'twitter': "https://twitter.com/emilyrodriguez",
            'order': 3,
            'image_url': profile_images[2]
        },
        {
            'name': "David Wilson",
            'position': "Customer Success Manager",
            'bio': "David ensures that both job seekers and employers have a positive experience using our platform.",
            'email': "david@searchfind.com",
            'linkedin': "https://linkedin.com/in/davidwilson",
            'twitter': "https://twitter.com/davidwilson",
            'order': 4,
            'image_url': profile_images[3]
        }
    ]

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

        # Download and save profile image
        if data['image_url']:
            try:
                response = requests.get(data['image_url'])
                if response.status_code == 200:
                    image_name = f"{data['name'].lower().replace(' ', '_')}.jpg"
                    team_member.photo.save(
                        image_name,
                        ContentFile(response.content),
                        save=True
                    )
                    print(f"Downloaded image for {data['name']}")
                else:
                    print(f"Failed to download image for {data['name']}: HTTP {response.status_code}")
            except Exception as e:
                print(f"Error downloading image for {data['name']}: {str(e)}")

    print(f"Created {len(team_members_data)} team members")

def create_trusted_companies():
    """Create sample trusted companies with actual logos."""
    print("Creating trusted companies...")

    # Sample company logo URLs (using placeholder images)
    company_logos = [
        "https://logo.clearbit.com/microsoft.com",
        "https://logo.clearbit.com/google.com",
        "https://logo.clearbit.com/amazon.com",
        "https://logo.clearbit.com/apple.com",
        "https://logo.clearbit.com/netflix.com",
        "https://logo.clearbit.com/adobe.com",
        "https://logo.clearbit.com/salesforce.com",
        "https://logo.clearbit.com/ibm.com"
    ]

    trusted_companies_data = [
        {
            'name': "Microsoft",
            'website': "https://microsoft.com",
            'order': 1,
            'logo_url': company_logos[0]
        },
        {
            'name': "Google",
            'website': "https://google.com",
            'order': 2,
            'logo_url': company_logos[1]
        },
        {
            'name': "Amazon",
            'website': "https://amazon.com",
            'order': 3,
            'logo_url': company_logos[2]
        },
        {
            'name': "Apple",
            'website': "https://apple.com",
            'order': 4,
            'logo_url': company_logos[3]
        },
        {
            'name': "Netflix",
            'website': "https://netflix.com",
            'order': 5,
            'logo_url': company_logos[4]
        },
        {
            'name': "Adobe",
            'website': "https://adobe.com",
            'order': 6,
            'logo_url': company_logos[5]
        },
        {
            'name': "Salesforce",
            'website': "https://salesforce.com",
            'order': 7,
            'logo_url': company_logos[6]
        },
        {
            'name': "IBM",
            'website': "https://ibm.com",
            'order': 8,
            'logo_url': company_logos[7]
        }
    ]

    for data in trusted_companies_data:
        # Check if company already exists
        company, created = TrustedCompany.objects.get_or_create(
            name=data['name'],
            defaults={
                'website': data['website'],
                'order': data['order'],
                'is_active': True
            }
        )

        # Download and save company logo
        if data['logo_url']:
            try:
                response = requests.get(data['logo_url'])
                if response.status_code == 200:
                    logo_name = f"{data['name'].lower().replace(' ', '_')}.png"
                    company.logo.save(
                        logo_name,
                        ContentFile(response.content),
                        save=True
                    )
                    print(f"Downloaded logo for {data['name']}")
                else:
                    print(f"Failed to download logo for {data['name']}: HTTP {response.status_code}")
            except Exception as e:
                print(f"Error downloading logo for {data['name']}: {str(e)}")

    print(f"Created {len(trusted_companies_data)} trusted companies")

def run():
    """Run the script to populate the database."""
    print("Starting to populate homepage data...")
    create_testimonials()
    create_team_members()
    create_trusted_companies()
    print("Finished populating homepage data!")

if __name__ == "__main__":
    run()
