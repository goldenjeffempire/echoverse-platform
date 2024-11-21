from django.contrib import admin
from .models import BlogPost, Profile, UserInteraction

admin.site.register(BlogPost)
admin.site.register(Profile)

class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'liked', 'flagged', 'created_at')
    list_filter = ('flagged',)

admin.site.register(UserInteraction, UserInteractionAdmin)
