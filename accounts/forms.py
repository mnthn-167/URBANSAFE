from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class UserRegisterForm(UserCreationForm):
    """Registration form for new users."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your email'
    }))
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'First name'
    }))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Last name'
    }))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Choose a username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Confirm password'})


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile."""
    class Meta:
        model = UserProfile
        fields = ['phone', 'location', 'latitude', 'longitude', 'alert_radius_km', 'profile_pic']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City or area'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Latitude', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Longitude', 'step': 'any'}),
            'alert_radius_km': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Alert radius (km)', 'min': 1, 'max': 100}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-input'}),
        }


class UserUpdateForm(forms.ModelForm):
    """Form for updating user info."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }
