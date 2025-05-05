import os
import requests
from PIL import Image
from io import BytesIO

# Create directories if they don't exist
os.makedirs('media/hero_images', exist_ok=True)

# Sample job-related image URLs
image_urls = [
    {
        'url': 'https://images.unsplash.com/photo-1521737711867-e3b97375f902?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1920&h=600&q=80',
        'filename': 'media/hero_images/jobs_hero_desktop.jpg',
        'description': 'Professional team in modern office (desktop)'
    },
    {
        'url': 'https://images.unsplash.com/photo-1521737711867-e3b97375f902?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=768&h=500&q=80',
        'filename': 'media/hero_images/jobs_hero_mobile.jpg',
        'description': 'Professional team in modern office (mobile)'
    },
    {
        'url': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1920&h=600&q=80',
        'filename': 'media/hero_images/companies_hero_desktop.jpg',
        'description': 'Business meeting with laptops (desktop)'
    },
    {
        'url': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=768&h=500&q=80',
        'filename': 'media/hero_images/companies_hero_mobile.jpg',
        'description': 'Business meeting with laptops (mobile)'
    },
    {
        'url': 'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1920&h=600&q=80',
        'filename': 'media/hero_images/home_hero_desktop.jpg',
        'description': 'Professional workspace with laptop (desktop)'
    },
    {
        'url': 'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=768&h=500&q=80',
        'filename': 'media/hero_images/home_hero_mobile.jpg',
        'description': 'Professional workspace with laptop (mobile)'
    }
]

# Download and save images
for image_data in image_urls:
    try:
        print(f"Downloading {image_data['description']}...")
        response = requests.get(image_data['url'])
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.save(image_data['filename'])
            print(f"Saved to {image_data['filename']}")
        else:
            print(f"Failed to download {image_data['url']}, status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {image_data['url']}: {str(e)}")

print("Download completed!")
