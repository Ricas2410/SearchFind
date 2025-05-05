from django import forms
from .models import JobListing, JobApplication, JobCategory, Company
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django_summernote.widgets import SummernoteWidget
from django_countries.widgets import CountrySelectWidget
import random
import string

class JobListingForm(forms.ModelForm):
    """Form for creating and updating job listings."""

    class Meta:
        model = JobListing
        fields = [
            'title', 'category', 'description', 'requirements', 'responsibilities',
            'location', 'is_remote', 'salary_min', 'salary_max', 'job_type', 'experience_level',
            'skills_required', 'application_deadline', 'application_url', 'cover_letter_required', 'is_featured'
        ]
        widgets = {
            'description': SummernoteWidget(attrs={'summernote': {'height': '300px', 'toolbar': [
                ['style', ['style']],
                ['font', ['bold', 'underline', 'clear']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['insert', ['link', 'hr']],
                ['view', ['fullscreen', 'codeview', 'help']],
            ]}}),
            'requirements': SummernoteWidget(attrs={'summernote': {'height': '300px', 'toolbar': [
                ['style', ['style']],
                ['font', ['bold', 'underline', 'clear']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['insert', ['link', 'hr']],
                ['view', ['fullscreen', 'codeview', 'help']],
            ]}}),
            'responsibilities': SummernoteWidget(attrs={'summernote': {'height': '300px', 'toolbar': [
                ['style', ['style']],
                ['font', ['bold', 'underline', 'clear']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['insert', ['link', 'hr']],
                ['view', ['fullscreen', 'codeview', 'help']],
            ]}}),
            'skills_required': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Enter skills separated by commas (e.g., Python, JavaScript, Project Management)')}),
            'application_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = _("Select a category")

        # Add company field if user has approved companies
        if self.user and self.user.owned_companies.filter(status='approved').exists():
            self.fields['company'] = forms.ModelChoiceField(
                queryset=self.user.owned_companies.filter(status='approved'),
                empty_label=_("Select a company"),
                required=True,
                widget=forms.Select(attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
                })
            )
        else:
            # If user has no approved companies, show a message in the form
            self.fields['company_message'] = forms.CharField(
                required=False,
                widget=forms.HiddenInput(),
                initial="You need to register and get approval for your company before posting jobs."
            )

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Set the posted_by to the current user
        if self.user and not instance.posted_by_id:
            instance.posted_by = self.user

        # If user has only one approved company and no company is selected, use that company
        if self.user and not instance.company_id:
            user_companies = self.user.owned_companies.filter(status='approved')
            if user_companies.count() == 1:
                instance.company = user_companies.first()

        # Generate a unique slug
        if not instance.slug:
            base_slug = slugify(instance.title)
            unique_slug = base_slug
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            unique_slug = f"{base_slug}-{suffix}"
            instance.slug = unique_slug

        if commit:
            instance.save()
        return instance

class JobApplicationForm(forms.ModelForm):
    """Form for submitting job applications."""
    use_profile_resume = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Use resume from my profile')
    )

    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': _('Tell us why you are a good fit for this position...'),
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
        }
        error_messages = {
            'resume': {
                'required': _('Please upload a resume or use your profile resume.'),
            },
            'cover_letter': {
                'required': _('Please provide a cover letter.'),
            }
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.job = kwargs.pop('job', None)
        super().__init__(*args, **kwargs)

        # If user doesn't have a resume in their profile, hide the checkbox
        if not (self.user and self.user.resume):
            self.fields['use_profile_resume'].widget = forms.HiddenInput()
            self.fields['use_profile_resume'].initial = False
            self.fields['resume'].required = True
        else:
            self.fields['resume'].required = False

        # Make cover letter required if the job requires it
        if self.job and self.job.cover_letter_required:
            self.fields['cover_letter'].required = True
        else:
            self.fields['cover_letter'].required = False

    def clean(self):
        cleaned_data = super().clean()
        use_profile_resume = cleaned_data.get('use_profile_resume', False)
        resume = cleaned_data.get('resume')

        # Check if either a resume is uploaded or profile resume is used
        if not use_profile_resume and not resume and not (self.user and self.user.resume):
            self.add_error('resume', _('Please upload a resume or use your profile resume.'))

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Set the applicant and job
        if self.user:
            instance.applicant = self.user
        if self.job:
            instance.job = self.job

        # Use profile resume if selected
        if self.user and self.cleaned_data.get('use_profile_resume', False) and self.user.resume:
            instance.resume = self.user.resume

        if commit:
            instance.save()
        return instance

class JobSearchForm(forms.Form):
    """Form for searching and filtering job listings."""

    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('Job title, keywords, or company'),
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('City, state, or zip code'),
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    category = forms.ModelChoiceField(
        queryset=JobCategory.objects.all(),
        required=False,
        empty_label=_("All Categories"),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    job_type = forms.MultipleChoiceField(
        choices=JobListing.JOB_TYPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'mr-2'
        })
    )

    experience_level = forms.MultipleChoiceField(
        choices=JobListing.EXPERIENCE_LEVEL_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'mr-2'
        })
    )

    min_salary = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': _('Minimum salary'),
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    max_salary = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': _('Maximum salary'),
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('Skills (comma separated)'),
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    is_remote = forms.BooleanField(
        required=False,
        label=_('Remote jobs only'),
        widget=forms.CheckboxInput(attrs={
            'class': 'mr-2'
        })
    )

    date_posted = forms.ChoiceField(
        choices=(
            ('', _('Any time')),
            ('1', _('Past 24 hours')),
            ('7', _('Past week')),
            ('30', _('Past month')),
        ),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    has_salary = forms.BooleanField(
        required=False,
        label=_('Show only jobs with salary'),
        widget=forms.CheckboxInput(attrs={
            'class': 'mr-2'
        })
    )

    exclude_expired = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Hide expired jobs'),
        widget=forms.CheckboxInput(attrs={
            'class': 'mr-2'
        })
    )

class CompanyForm(forms.ModelForm):
    """Form for creating and editing companies."""
    class Meta:
        model = Company
        fields = [
            'name', 'logo', 'cover_image', 'website', 'description', 'short_description',
            'industry', 'other_industry', 'company_size', 'founded_year', 'country', 'headquarters', 'specialties',
            'facebook', 'twitter', 'linkedin', 'instagram'
        ]
        widgets = {
            'description': SummernoteWidget(attrs={'summernote': {'height': '300px', 'toolbar': [
                ['style', ['style']],
                ['font', ['bold', 'underline', 'clear']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['insert', ['link', 'hr']],
                ['view', ['fullscreen', 'codeview', 'help']],
            ]}}),
            'short_description': forms.TextInput(attrs={
                'placeholder': 'Brief description of your company (max 255 characters)',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'industry': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 select2-industry',
                'data-placeholder': 'Select or type an industry'
            }),
            'other_industry': forms.TextInput(attrs={
                'placeholder': 'Specify your industry if not in the list above',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 other-industry-field',
                'style': 'display: none;'
            }),
            'country': CountrySelectWidget(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 select2-country',
                'data-placeholder': 'Select a country'
            }),
            'specialties': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter specialties separated by commas',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'founded_year': forms.NumberInput(attrs={
                'min': 1800,
                'max': 2100,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            }),
        }
        help_texts = {
            'logo': _('Company logo (recommended size: 200x200px)'),
            'cover_image': _('Cover image for company profile (recommended size: 1200x300px)'),
            'specialties': _('Enter specialties separated by commas'),
            'country': _('Select the country where your company is based'),
            'headquarters': _('City or specific location'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make certain fields required
        self.fields['description'].required = True
        self.fields['industry'].required = True
        self.fields['company_size'].required = True
        self.fields['headquarters'].required = True

        # Set up conditional display for other_industry field
        if self.instance and self.instance.industry == 'other':
            self.fields['other_industry'].widget.attrs['style'] = 'display: block;'
            self.fields['other_industry'].required = True
        else:
            self.fields['other_industry'].widget.attrs['style'] = 'display: none;'
            self.fields['other_industry'].required = False

        # Add styling to all form fields
        for field_name, field in self.fields.items():
            if field_name not in ['description', 'logo', 'cover_image', 'industry', 'country', 'other_industry']:  # Skip fields with custom widgets
                css_class = 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'

                if field.widget.attrs.get('class'):
                    field.widget.attrs['class'] += f' {css_class}'
                else:
                    field.widget.attrs['class'] = css_class

                # Add placeholder for text fields
                if isinstance(field.widget, forms.TextInput) and not field.widget.attrs.get('placeholder'):
                    field.widget.attrs['placeholder'] = f'Enter {field_name.replace("_", " ").title()}'
                elif isinstance(field.widget, forms.URLInput) and not field.widget.attrs.get('placeholder'):
                    field.widget.attrs['placeholder'] = f'https://...'
