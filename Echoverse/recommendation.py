import random
from .models import BlogPost, UserInteraction
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_posts_for_user(user):
    # Get posts the user has interacted with
    user_interactions = UserInteraction.objects.filter(user=user)
    liked_posts = user_interactions.filter(liked=True).values_list('post', flat=True)
    viewed_posts = user_interactions.filter(viewed=True).values_list('post', flat=True)

    # Recommend posts based on liked and viewed posts, excluding those already liked/viewed
    recommended_posts = BlogPost.objects.exclude(id__in=liked_posts).exclude(id__in=viewed_posts)

    # Return a random sample of recommended posts
    return recommended_posts.order_by('?')[:5]

def get_similar_posts(post_id):
    """
    Recommend similar blog posts based on the content of the given blog post.
    Returns a list of recommended blog post titles.
    """
    # Fetch all blog posts from the database
    posts = BlogPost.objects.all()
    titles = [post.title for post in posts]
    contents = [post.content for post in posts]

    # Convert contents into a matrix of TF-IDF features
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(contents)

    # Get the index of the current post
    post_idx = titles.index(BlogPost.objects.get(id=post_id).title)

    # Compute cosine similarity between the given post and all other posts
    cosine_similarities = cosine_similarity(tfidf_matrix[post_idx], tfidf_matrix)

    # Get indices of the most similar posts
    similar_indices = cosine_similarities.argsort()[0][-6:-1]  # Top 5 similar posts (excluding the current one)

    # Get the titles of the similar posts
    similar_posts = [titles[i] for i in similar_indices]

    return similar_posts
