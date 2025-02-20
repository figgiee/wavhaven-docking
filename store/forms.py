from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Beat, UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'search-input w-full hover-scale-sm',
            'placeholder': 'Enter your email'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

class BeatForm(forms.ModelForm):
    class Meta:
        model = Beat
        fields = ['title', 'price', 'audio_file', 'tags']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-input rounded-lg'})
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'display_name', 'avatar', 'bio', 'location', 'website',
            'soundcloud_link', 'bandcamp_link', 'youtube_link',
            'spotify_link', 'twitter_link', 'instagram_link',
            'facebook_link', 'genres'
        ]
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-input rounded-lg'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea rounded-lg', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-input rounded-lg'}),
            'website': forms.URLInput(attrs={'class': 'form-input rounded-lg'}),
            'soundcloud_link': forms.URLInput(attrs={'class': 'form-input rounded-lg'}),
            'bandcamp_link': forms.URLInput(attrs={'class': 'form-input rounded-lg'}),
            'youtube_link': forms.URLInput(attrs={'class': 'form-input rounded-lg'}),
            'spotify_link': forms.URLInput(attrs={'class': 'form-input rounded-lg'}),
            'twitter_link': forms.URLInput(attrs={'class': 'form-input rounded-lg'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-input rounded-lg'}),
            'facebook_link': forms.URLInput(attrs={'class': 'form-input rounded-lg'}),
            'genres': forms.SelectMultiple(attrs={'class': 'form-multiselect rounded-lg'})
        }
