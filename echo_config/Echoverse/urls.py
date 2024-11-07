from django.urls import path
from .views import post_list, register, login_view, logout_view, create_post, edit_post, delete_post, post_detail, profile_view, edit_profile, CustomLoginView, CustomLogoutView, moderate_comments, comment_view, search_posts
from . import views

urlpatterns = [
    path('', post_list, name='post_list'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('post/', views.post_list, name='post_list'),
    path('create/', create_post, name='create_post'),
    path('edit/<int:post_id>/', edit_post, name='edit_post'),
    path('delete/<int:post_id>/', delete_post, name='delete_post'),
    path('post/<int:id>/', post_detail, name='post_detail'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('moderate_comments/', moderate_comments, name='moderate_comments'),
    path('comment/', comment_view, name='comment'),
    path('search/', views.search_posts, name='search_posts'),
]
