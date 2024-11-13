from django.urls import path
from .views import post_list, register, login_view, logout_view, create_post, edit_post, delete_post, post_detail, profile_view, edit_profile, CustomLoginView, CustomLogoutView, moderate_comments, comment_view, search_posts, add_comment, like_post
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', post_list, name='post_list'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('posts/', post_list, name='post_list'),
    path('create_post/', create_post, name='create_post'),
    path('edit_post/<int:post_id>/', edit_post, name='edit_post'),
    path('delete_post/<int:post_id>/', delete_post, name='delete_post'),
    path('posts/<int:id>/', post_detail, name='post_detail'),
    path('profile/', profile_view, name='profile_view'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('moderate_comments/', moderate_comments, name='moderate_comments'),
    path('comment/', comment_view, name='comment'),
    path('posts/<int:post_id>/like/', like_post, name='like_post'),
    path('posts/<int:post_id>/add_comment/', add_comment, name='add_comment'),
    path('search/', views.search_posts, name='search_posts'),
    path('login/', auth_views.LoginView.as_view(template_name='echoverse/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='post_list'), name='logout'),
]
