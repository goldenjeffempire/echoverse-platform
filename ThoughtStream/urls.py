from django.urls import path
from .views import (
    home,
    signup,
    profile_view,
    contact_view,
    PostListView,
    PostCreateView,
    PostDetailView,
    PostUpdateView,
    PostDeleteView,
    PostSearchView,
)

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('profile/', profile_view, name='profile'),
    path('contact/', contact_view, name='contact'),
    path('posts/', PostListView.as_view(), name='post_list'),
    path('post/new/', views.create_post, name='create_post'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('search/', PostSearchView.as_view(), name='post-search'),
]
