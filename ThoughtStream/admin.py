from django.contrib import admin
from django.contrib.auth.models import User
from .models import Post

# Admin view for managing posts
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    list_filter = ('author', 'created_at')

# Register the Post model with the custom admin
admin.site.register(Post, PostAdmin)

# Admin view for managing users
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    search_fields = ('username', 'email')

# Unregister the default User admin and register your custom UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
