import openai
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import BlogPost, Category, UserInteraction, Profile, Comment, Like, Rating, Review
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from .forms import BlogPostForm, CommentForm, ProfileForm, SignupForm, SearchForm, AIContentForm, RatingForm, ReviewForm
from django.core.paginator import Paginator
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.core.mail import send_mail
from .moderation import moderate_content
from .recommendation import recommend_posts_for_user
from .ai_content import generate_blog_post
from .utils import get_similar_posts

openai.api_key = settings.OPENAI_API_KEY

def generate_personalized_recommendations(user, post_content):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Suggest blog posts related to this content: {post_content}",
        max_tokens=150
    )

    user_interactions = UserInteraction.objects.filter(user=user)
    interacted_posts = [interaction.post for interaction in user_interactions]

    similar_posts = Post.objects.filter(id__in=[post.id for post in interacted_posts])

    ai_recommendations = generate_recommendations(post_content)
    personalized_recommendations = similar_posts

    recommendations = response.choices[0].text.strip()
    return ai_recommendations, personalized_recommendations

def generate_content(request):
    generated_content = None
    if request.method == 'POST':
        form = AIContentForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['prompt']
            generated_content = generate_blog_post(prompt)
    else:
        form = AIContentForm()

    return render(request, 'echoverse/generate_content.html', {'form': form, 'generated_content': generated_content})

def some_view(request):
    from Echoverse.forms import CustomSignupForm
    form = CustomSignupForm()
    return render(request, 'some_template.html', {'form': form})

def post_list(request):
    query = request.GET.get('q')
    if query:
        posts = BlogPost.objects.filter(title__icontains=query)
    else:
        posts = BlogPost.objects.all().order_by('-created_at')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'echoverse/post_list.html', {
        'posts': page_obj,
        'query': query,
    })

class SignUpView(CreateView):
    form_class = SignupForm
    template_name = 'echoverse/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        send_mail(
            'Welcome to EchoVerse!',
            'Thank you for signing up.',
            'from@example.com',
            [form.cleaned_data['email']],
            fail_silently=False,
        )
        return super().form_valid(form)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if not hasattr(user, 'profile'):
                    Profile.objects.create(user=user)
                return redirect('post_list')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'echoverse/login.html', {'form': form})
class CustomLoginView(LoginView):
    template_name = 'echoverse/login.html'
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'echoverse/password_change.html'
    success_url = '/profile/'

    def form_valid(self, form):
        response = super().form_valid(form)

        if not hasattr(self.request.user, 'profile'):
            Profile.objects.create(user=self.request.user)

        return response

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)

def logout_view(request):
    logout(request)
    return redirect('post_list')
class CustomLogoutView(LogoutView):
    next_page = 'post_list'

@login_required
def create_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')
    else:
        form = BlogPostForm()
    return render(request, 'echoverse/create_post.html', {'form': form})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    if post.author != request.user:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('post_list')

    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect('post_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BlogPostForm(instance=post)

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
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, id=post_id)
    if post.author != request.user:
        return redirect('post_list')
    if request.method == 'POST':
        post.delete()
        return redirect('post_list')
    return render(request, 'echoverse/delete_post.html', {'post': post})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    tags = generate_tags(post.content)
    for tag_name in tags:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        post.tags.add(tag)

    ai_recommendations, personalized_recommendations = generate_personalized_recommendations(request.user, post.content)
    recommended_posts = generate_recommendations(post.content)
    similar_posts = Post.objects.filter(title__icontains=recommended_posts[:100])[:5]

    if request.user.is_authenticated:
        user_interaction, created = UserInteraction.objects.get_or_create(user=request.user, post=post)
        user_interaction.viewed = True
        user_interaction.save()

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
        'similar_posts': similar_posts,
        'ai_recommendations': ai_recommendations,
        'personalized_recommendations': personalized_recommendations,
        'tags': post.tags.all()
    })

def blog_post_detail(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk)
    blog_post.views += 1
    blog_post.save()
    comments = blog_post.comments.all()
    ratings = blog_post.ratings.all()
    reviews = blog_post.reviews.all()

    similar_posts = blog_post.get_similar_posts()
    recommended_posts = get_similar_posts(pk)

    comment_form = CommentForm(request.POST or None)
    rating_form = RatingForm(request.POST or None)
    review_form = ReviewForm(request.POST or None)

    if request.method == 'POST' and 'comment_submit' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.blog_post = blog_post
            comment.author = request.user
            try:
                comment.save()
            except ValueError as e:
                messages.error(request, str(e))
                return redirect("blog_post_detail", pk=pk)
        elif rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.blog_post = blog_post
            rating.author = request.user
            rating.save()
        elif review_form.is_valid():
            review = review_form.save(commit=False)
            review.blog_post = blog_post
            review.author = request.user
            review.save()
        return redirect('blog_post_detail', pk=pk)

    average_rating = blog_post.ratings.aggregate(models.Avg('score'))['score__avg'] or 0

    return render(request, 'echoverse/blog_post_detail.html', {
        'blog_post': blog_post,
        'comments': blog_post.comments.all(),
        'ratings': ratings,
        'reviews': reviews,
        'similar_posts': similar_posts,
        "recommended_posts": recommended_posts,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'review_form': review_form
    })

def blog_post_list(request):
    form = SearchForm(request.GET)
    posts = BlogPost.objects.all()

    if form.is_valid() and form.cleaned_data['query']:
        query = form.cleaned_data['query']
        posts = posts.filter(title__icontains=query) | posts.filter(content__icontains=query)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "blog_post_list.html", {
        "form": form,
        "posts": posts,
        "page_obj": page_obj,
    })

def post_interaction(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    comment = request.POST.get('comment', '')
    if comment and moderate_content(comment):
        # If flagged, show an error message
        return render(request, 'echoverse/post_detail.html', {
            'post': post,
            'error_message': 'Your comment has been flagged due to inappropriate content.'
        })

    user_interaction, created = UserInteraction.objects.get_or_create(user=user, post=post)

    if 'like' in request.POST:
        user_interaction.liked = not user_interaction.liked
    if comment:
        user_interaction.comment = comment

    user_interaction.save()

    return JsonResponse({
        'liked': interaction.liked,
        'comment': interaction.comment,
        'post_detail': post_id
    })

@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'echoverse/profile.html', {'form': form, 'profile': profile})

@login_required
def user_dashboard(request):
    user_interactions = UserInteraction.objects.filter(user=request.user)
    recommended_posts = recommend_posts_for_user(request.user)

    context = {
        'interactions': user_interactions,
        'recommended_posts': recommended_posts,
    }
    return render(request, 'echoverse/user_dashboard.html', context)

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

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('post_list')
    else:
        form = CommentForm()
    return render(request, 'echoverse/add_comment.html', {'form': form, 'post': post})

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return HttpResponseForbidden("You are not allowed to edit this comment.")

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('view_post', post_id=comment.post.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'echoverse/edit_comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return HttpResponseForbidden("You are not allowed to delete this comment.")

    post_id = comment.post.id
    comment.delete()
    return redirect('view_post', post_id=post_id)

@login_required
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    return render(request, 'echoverse/view_post.html', {'post': post, 'comments': comments})

def comment_view(request, post_id=None):
    if post_id:
        post = get_object_or_404(Post, id=post_id)
    else:
        post = None

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            if post:
                comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('post_detail', pk=post.id if post else 'post_list')
    else:
        form = CommentForm()

    return render(request, 'echoverse/comment.html', {'form': form, 'post': post})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return redirect('post_detail', pk=post.id)

def search_posts(request):
    query = request.GET.get('q')
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    return render(request, 'echoverse/search.html', {'form': form, 'results': results})

def generate_tags(post_content):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Generate tags for the following blog post content: {post_content}",
        max_tokens=50
    )

    tags_text = response.choices[0].text.strip()
    tags = [tag.strip() for tag in tags_text.split(',')]
    return tags

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    tags = generate_tags(post.content)
    for tag_name in tags:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        post.tags.add(tag)

    recommended_posts = generate_recommendations(post.content)
    similar_posts = Post.objects.filter(title__icontains=recommended_posts[:100])[:5]

    return render(request, 'echoverse/post_detail.html', {
        'post': post,
        'similar_posts': similar_posts,
        'recommendations': recommended_posts,
        'tags': post.tags.all()
    })
