import random
from .models import BlogPost, UserInteraction

def recommend_posts_for_user(user):
    # Get posts the user has interacted with
    user_interactions = UserInteraction.objects.filter(user=user)
    liked_posts = user_interactions.filter(liked=True).values_list('post', flat=True)
    viewed_posts = user_interactions.filter(viewed=True).values_list('post', flat=True)

    # Recommend posts based on liked and viewed posts, excluding those already liked/viewed
    recommended_posts = BlogPost.objects.exclude(id__in=liked_posts).exclude(id__in=viewed_posts)

    # Return a random sample of recommended posts
    return recommended_posts.order_by('?')[:5]
