from django import forms
from .models import Message, Connection
from django.utils.translation import gettext_lazy as _

class MessageForm(forms.ModelForm):
    """Form for sending messages."""
    
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': _('Type your message here...'),
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
        }
        
class ConnectionRequestForm(forms.Form):
    """Form for sending connection requests."""
    
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3, 
            'placeholder': _('Add a personal note to your connection request...'),
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        }),
    )
