from django.http import HttpResponse
from django.conf import settings
from django.template.loader import render_to_string

def robots_txt(request):
    """
    Generate a robots.txt file dynamically.
    """
    site_url = settings.SITE_URL
    context = {'site_url': site_url}
    content = render_to_string('robots.txt', context)
    return HttpResponse(content, content_type='text/plain')
