from django import forms
from .models import Incident, Comment


class IncidentForm(forms.ModelForm):
    """Form for reporting a new incident."""
    class Meta:
        model = Incident
        fields = ['title', 'description', 'category', 'severity', 'address', 'latitude', 'longitude', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Brief title of the incident'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Describe the incident in detail...',
                'rows': 5
            }),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'severity': forms.Select(attrs={'class': 'form-input'}),
            'address': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Location address'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Latitude',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Longitude',
                'step': 'any'
            }),
            'photo': forms.FileInput(attrs={'class': 'form-input'}),
        }


class CommentForm(forms.ModelForm):
    """Form for adding a comment to an incident."""
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Add your comment or offer help...',
                'rows': 3
            }),
        }
