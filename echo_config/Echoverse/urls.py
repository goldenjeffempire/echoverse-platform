from django.urls import path
from .views import post_list, register, login_view, logout_view, create_post, edit_post, delete_post,

urlpatterns = [
    path('', post_list, name='post_list'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('create/', create_post, name='create_post'),
    path('edit/<int:post_id>/', edit_post, name='edit_post'),
    path('delete/<int:post_id>/', delete_post, name='delete_post'),
]

