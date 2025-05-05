from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import JobListing, JobCategory, Company


class JobListingSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return JobListing.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at


class JobCategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return JobCategory.objects.all()


class CompanySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Company.objects.filter(status='approved')

    def lastmod(self, obj):
        return obj.updated_at


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return [
            'jobs:home', 
            'jobs:job_list', 
            'jobs:company_list',
            'jobs:about',
            'jobs:contact',
            'jobs:terms',
            'jobs:privacy',
            'jobs:faq',
        ]

    def location(self, item):
        return reverse(item)


sitemaps = {
    'jobs': JobListingSitemap,
    'categories': JobCategorySitemap,
    'companies': CompanySitemap,
    'static': StaticViewSitemap,
}
