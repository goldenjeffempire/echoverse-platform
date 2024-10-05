from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Comment, UserProfile, Post
from django.core.exceptions import ValidationError

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required. Please provide a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if the email already exists in the User model
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with that username already exists.")

        return username

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment here...'}),
        }

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Search...'}))

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture']

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
