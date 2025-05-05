from django.core.management.base import BaseCommand
from django.utils.text import slugify
from jobs.models import JobCategory

class Command(BaseCommand):
    help = 'Creates initial data for the job board'

    def handle(self, *args, **options):
        # Create job categories
        categories = [
            {
                'name': 'Information Technology',
                'description': 'Jobs in software development, IT support, cybersecurity, and other tech fields.'
            },
            {
                'name': 'Engineering',
                'description': 'Jobs in various engineering disciplines including mechanical, electrical, civil, and chemical engineering.'
            },
            {
                'name': 'Marketing',
                'description': 'Jobs in digital marketing, content creation, SEO, social media, and brand management.'
            },
            {
                'name': 'Finance',
                'description': 'Jobs in accounting, financial analysis, banking, investment, and financial planning.'
            },
            {
                'name': 'Healthcare',
                'description': 'Jobs in medical, nursing, pharmacy, and other healthcare-related fields.'
            },
            {
                'name': 'Education',
                'description': 'Jobs in teaching, training, educational administration, and curriculum development.'
            },
            {
                'name': 'Sales',
                'description': 'Jobs in sales, business development, account management, and customer success.'
            },
            {
                'name': 'Human Resources',
                'description': 'Jobs in recruitment, HR management, employee relations, and talent development.'
            },
            {
                'name': 'Design',
                'description': 'Jobs in graphic design, UX/UI design, product design, and creative direction.'
            },
            {
                'name': 'Customer Service',
                'description': 'Jobs in customer support, client relations, and customer experience management.'
            },
        ]
        
        for category_data in categories:
            category, created = JobCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'slug': slugify(category_data['name']),
                    'description': category_data['description']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(f'Category already exists: {category.name}')
        
        self.stdout.write(self.style.SUCCESS('Initial data created successfully!'))
