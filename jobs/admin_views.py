from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.core.management import call_command
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.html import format_html

from .models import Newsletter, JobListing

@staff_member_required
def send_newsletter_view(request):
    """Admin view for sending newsletters to subscribers."""
    active_subscribers_count = Newsletter.objects.filter(is_active=True).count()
    recent_jobs = JobListing.objects.filter(status='published').order_by('-created_at')[:10]
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        days = request.POST.get('days', '7')
        limit = request.POST.get('limit', '10')
        test_email = request.POST.get('test_email', '')
        
        if not subject:
            messages.error(request, _('Please provide a subject for the newsletter.'))
            return redirect('admin:send_newsletter')
        
        try:
            days = int(days)
            limit = int(limit)
            
            # Call the management command
            cmd_args = [
                '--subject', subject,
                '--days', str(days),
                '--limit', str(limit),
            ]
            
            if message:
                cmd_args.extend(['--message', message])
                
            if test_email:
                cmd_args.extend(['--test-email', test_email])
                messages.info(request, _('Sending test email to {0}').format(test_email))
            else:
                messages.info(request, _('Sending newsletter to {0} subscribers').format(active_subscribers_count))
            
            call_command('send_newsletter', *cmd_args)
            
            if test_email:
                messages.success(request, _('Test newsletter sent successfully!'))
            else:
                messages.success(request, _('Newsletter sent successfully to {0} subscribers!').format(active_subscribers_count))
            
        except Exception as e:
            messages.error(request, _('Error sending newsletter: {0}').format(str(e)))
    
    context = {
        'title': _('Send Newsletter'),
        'active_subscribers_count': active_subscribers_count,
        'recent_jobs': recent_jobs,
        'has_permission': True,
        'opts': Newsletter._meta,
        'site_title': admin.site.site_title,
        'site_header': admin.site.site_header,
    }
    
    return render(request, 'admin/send_newsletter.html', context)

class NewsletterAdminSite(admin.AdminSite):
    """Custom admin site with additional views."""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-newsletter/', self.admin_view(send_newsletter_view), name='send_newsletter'),
        ]
        return custom_urls + urls
