from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, UserProfile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from .forms import PostForm
from django.core.paginator import Paginator
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

def post_list(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'echoverse/post_list.html', {'posts': posts})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('post_list')
    else:
        form = UserCreationForm()
    return render(request, 'echoverse/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('post_list')
    else:
        form = AuthenticationForm()
    return render(request, 'echoverse/login.html', {'form': form})
class CustomLoginView(LoginView):
    template_name = 'echoverse/login.html'

def logout_view(request):
    logout(request)
    return redirect('post_list')

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'echoverse/create_post.html', {'form': form})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('post_list')
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'echoverse/edit_post.html', {'form': form})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('post_list')
    if request.method == 'POST':
        post.delete()
        return redirect('post_list')
    return render(request, 'echoverse/delete_post.html', {'post': post})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'echoverse/post_detail.html', {'post': post})

@login_required
def profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        location = request.POST.get('location', '')
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        return redirect('profile')
    return render(request, 'echoverse/profile.html', {'profile': user_profile})
