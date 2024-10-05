from django.urls import path
from . import views
from .views import (
    PostDetailView, 
    PostListView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    PostSearchView,
    home,
    signup,
    profile_view,
    contact_view,
)

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('profile/', profile_view, name='profile'),
    path('contact/', contact_view, name='contact'),
    path('posts/', PostListView.as_view(), name='post_list'),
    path('post/new/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('search/', PostSearchView.as_view(), name='post_search'),
]

