from django import forms
from django.utils.translation import gettext_lazy as _
from .models import SubscriptionPlan, UserSubscription
from .ai_models import ResumeBuilder


class SubscriptionPlanForm(forms.ModelForm):
    """Form for creating and updating subscription plans."""
    class Meta:
        model = SubscriptionPlan
        fields = [
            'name', 'plan_type', 'description', 'price', 'duration_days',
            'resume_builder', 'resume_review', 'job_match_recommendations', 'company_recommendations',
            'featured_jobs', 'priority_listing', 'candidate_matching', 'advanced_analytics',
            'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ResumeBuilderForm(forms.ModelForm):
    """Form for AI resume builder."""
    class Meta:
        model = ResumeBuilder
        fields = ['original_content', 'job_listing']
        widgets = {
            'original_content': forms.Textarea(attrs={
                'rows': 10,
                'placeholder': _('Paste your current resume content here...')
            }),
        }


class ResumeUploadForm(forms.Form):
    """Form for uploading a resume for AI analysis."""
    resume_file = forms.FileField(
        label=_('Upload Resume'),
        help_text=_('Upload your resume for AI analysis (PDF, DOCX, or TXT)'),
        widget=forms.FileInput(attrs={'accept': '.pdf,.docx,.doc,.txt'})
    )
    
    def clean_resume_file(self):
        resume_file = self.cleaned_data.get('resume_file')
        if resume_file:
            # Check file extension
            allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
            file_extension = resume_file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(_('Invalid file format. Please upload a PDF, DOCX, or TXT file.'))
            
            # Check file size (max 5MB)
            if resume_file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_('File size too large. Maximum file size is 5MB.'))
        
        return resume_file


class PaymentForm(forms.Form):
    """Form for payment processing."""
    amount = forms.DecimalField(
        label=_('Amount'),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': '0.00'})
    )
    reference = forms.CharField(
        label=_('Reference'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Automatically generated if empty'})
    )
    email = forms.EmailField(
        label=_('Email'),
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'user@example.com'})
    )
    first_name = forms.CharField(
        label=_('First Name'),
        max_length=100,
        required=False
    )
    last_name = forms.CharField(
        label=_('Last Name'),
        max_length=100,
        required=False
    )
    subscription_plan = forms.ModelChoiceField(
        label=_('Subscription Plan'),
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['email'].initial = user.email
            if hasattr(user, 'first_name'):
                self.fields['first_name'].initial = user.first_name
            if hasattr(user, 'last_name'):
                self.fields['last_name'].initial = user.last_name


class SalaryInsightsForm(forms.Form):
    """Form for salary insights request."""
    job_title = forms.CharField(
        label=_('Job Title'),
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Software Engineer'})
    )
    location = forms.CharField(
        label=_('Location'),
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Lagos, Nigeria'})
    )
    experience_level = forms.ChoiceField(
        label=_('Experience Level'),
        choices=[
            ('entry_level', _('Entry Level (0-2 years)')),
            ('mid_level', _('Mid Level (3-5 years)')),
            ('senior', _('Senior (6-10 years)')),
            ('expert', _('Expert (10+ years)'))
        ],
        required=True
    )
    industry = forms.CharField(
        label=_('Industry'),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Technology'})
    )


class PaystackConfigForm(forms.Form):
    """Form for configuring Paystack settings."""
    public_key = forms.CharField(
        label=_('Paystack Public Key'),
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'pk_test_...'})
    )
    secret_key = forms.CharField(
        label=_('Paystack Secret Key'),
        max_length=255,
        widget=forms.PasswordInput(attrs={'placeholder': 'sk_test_...'})
    )
    webhook_secret = forms.CharField(
        label=_('Webhook Secret'),
        max_length=255,
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'whsec_...'})
    )
    is_live = forms.BooleanField(
        label=_('Live Mode'),
        required=False,
        help_text=_('Check to use live mode instead of test mode')
    )
    currency = forms.ChoiceField(
        label=_('Currency'),
        choices=[
            ('USD', 'USD - US Dollar'),
            ('NGN', 'NGN - Nigerian Naira'),
            ('GHS', 'GHS - Ghanaian Cedi'),
            ('ZAR', 'ZAR - South African Rand'),
            ('EUR', 'EUR - Euro'),
            ('GBP', 'GBP - British Pound'),
        ]
    )
