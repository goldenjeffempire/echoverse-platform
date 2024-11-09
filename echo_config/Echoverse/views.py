from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Profile, Comment, Like
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth import authenticate, login, logout
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

def post_list(request):
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(title__icontains=query)
    else:
        posts = Post.objects.all().order_by('-created_at')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'echoverse/post_list.html', {
        'posts': page_obj,
        'query': query,
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
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
class CustomLogoutView(LogoutView):
    next_page = 'post_list'

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
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('post_list')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect('post_detail', pk=post.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PostForm(instance=post)

    return render(request, 'echoverse/edit_post.html', {'form': form, 'post': post})


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile_view')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'echoverse/edit_profile.html', {'form': form})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('post_list')
    if request.method == 'POST':
        post.delete()
        return redirect('post_list')
    return render(request, 'echoverse/delete_post.html', {'post': post})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    liked = post.likes.filter(user=request.user).exists()

    if request.method == 'POST':
        if 'like' in request.POST:
            if not liked:
                Like.objects.create(post=post, user=request.user)
        elif 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.user = request.user
                comment.save()
                return redirect('post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()

    return render(request, 'echoverse/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'liked': liked,
    })


@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'echoverse/profile.html', {'profile': user_profile})

@login_required
@login_required
def edit_post(request, pk):
    """
    Handles editing of a post by the logged-in user.
    """
    post = get_object_or_404(Post, pk=pk)

    # Ensure the logged-in user is the author of the post
    if post.author != request.user:
        messages.error(request, 'You are not authorized to edit this post.')
        return redirect('post_list')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'The post has been successfully updated.')
            return redirect('post_list')
        else:
            messages.error(request, 'There was an error updating the post. Please try again.')
    else:
        form = PostForm(instance=post)

    return render(request, 'echoverse/edit_post.html', {'form': form, 'post': post})

@staff_member_required
def moderate_comments(request):
    comments = Comment.objects.all()

    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        comment = Comment.objects.get(id=comment_id)

        if 'approve' in request.POST:
            comment.approved = True
            comment.save()
        elif 'disapprove' in request.POST:
            comment.approved = False
            comment.save()

        return redirect('moderate_comments')

    return render(request, 'echoverse/moderate_comments.html', {'comments': comments})

def comment_view(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.save()
            return redirect('post_list')
    else:
        form = CommentForm()
    return render(request, 'echoverse/comment.html', {'form': form})

def search_posts(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    return render(request, 'echoverse/search_results.html', {'results': results, 'query': query})
