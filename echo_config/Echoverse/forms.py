from django import forms
from .models import Post, Comment, UserProfile, Tag

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'tags']
        widgets = {'tags': forms.CheckboxSelectMultiple}

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture']
