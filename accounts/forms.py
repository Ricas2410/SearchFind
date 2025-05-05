from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new user. Extends Django's UserCreationForm.
    """
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        required=True,
        label=_('I am a'),
        widget=forms.RadioSelect
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'user_type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['username'].required = False
        self.fields['username'].help_text = _('Optional. If left blank, a username will be generated from your email.')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')

        # If username is not provided, generate one from email
        if not username and email:
            import uuid
            # Use the part before @ in email, and add a random suffix
            base_username = email.split('@')[0]
            # Ensure username is unique by adding a short UUID
            unique_id = str(uuid.uuid4())[:8]
            username = f"{base_username}_{unique_id}"
            cleaned_data['username'] = username
            self.instance.username = username

        return cleaned_data

class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating user information. Extends Django's UserChangeForm.
    """
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name')

class JobSeekerProfileForm(forms.ModelForm):
    """
    Form for updating job seeker profile information.
    """
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text=_('Enter your skills separated by commas (e.g., Python, JavaScript, Project Management)')
    )

    experience = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        help_text=_('Describe your work experience')
    )

    education = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        help_text=_('Describe your educational background')
    )

    job_title = forms.CharField(
        max_length=255,
        required=False,
        help_text=_('Your current or desired job title')
    )

    location = forms.CharField(
        max_length=255,
        required=False,
        help_text=_('Your location (city, country)')
    )

    class Meta:
        model = CustomUser
        fields = ('phone_number', 'bio', 'profile_picture', 'resume', 'skills', 'job_title', 'location', 'experience', 'education')

class EmployerProfileForm(forms.ModelForm):
    """
    Form for updating employer profile information.
    """
    class Meta:
        model = CustomUser
        fields = ('phone_number', 'company_name', 'company_website', 'company_description', 'company_logo')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company_name'].required = True
