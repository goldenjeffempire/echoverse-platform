from django import forms
from .models import Post, Comment, Profile, Tag

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
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
