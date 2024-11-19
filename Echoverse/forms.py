from django import forms
from .models import BlogPost, Comment, Profile, Tag
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'tags']
        widgets = {'tags': forms.CheckboxSelectMultiple}

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'location', 'birth_date']

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)

class SignupForm(UserCreationForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, request):
        user = super().save(request)
        user.email = self.cleaned_data['email']
        user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
