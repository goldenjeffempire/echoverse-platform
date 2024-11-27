from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def validate_image(file):
    """Validator to ensure only valid image files are uploaded."""
    valid_extensions = ('.png', '.jpg', '.jpeg')
    if not file.name.lower().endswith(valid_extensions):
        raise ValidationError("Only .png, .jpg, and .jpeg formats are supported.")


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, validators=[validate_image])
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'


@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """Signal to create or save user profile on user save."""
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True, validators=[validate_image])
    views = models.PositiveIntegerField(default=0)
    ratings = models.ManyToManyField(
        'Rating',
        related_name='rated_blog_posts',
        blank=True
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

    def get_similar_posts(self):
        """Calculate and return similar posts based on cosine similarity of ratings."""
        all_posts = BlogPost.objects.all()
        ratings_matrix = np.array([post.get_ratings_vector() for post in all_posts])
        similarity_matrix = cosine_similarity(ratings_matrix)
        similar_posts = similarity_matrix[self.pk]

        sorted_posts = sorted(enumerate(similar_posts), key=lambda x: x[1], reverse=True)[1:6]

        return [all_posts[i[0]] for i in sorted_posts]

    def get_ratings_vector(self):
        """Return a vector of ratings for similarity calculations."""
        ratings_vector = []
        for user in User.objects.all():
            try:
                rating = self.ratings.get(author=user).rating
            except Rating.DoesNotExist:
                rating = 0
            ratings_vector.append(rating)
        return ratings_vector


class Rating(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='authored_ratings'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_ratings',
        null=True,
        blank=True
    )
    score = models.PositiveIntegerField(default=0)
    review = models.TextField()
    post = models.ForeignKey(
        BlogPost,
        related_name='ratings_for_post',
        on_delete=models.CASCADE
    )
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        choices=[
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5'),
        ],
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Rating by {self.user.username} for {self.post.title}"


class Comment(models.Model):
    post = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'


class Like(models.Model):
    post = models.ForeignKey(BlogPost, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['post', 'user'], name='unique_post_user_like')
        ]

    def __str__(self):
        return f'Like by {self.user.username} on {self.post.title}'


class UserInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)
    viewed = models.BooleanField(default=False)
    flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.post.title}'


class Review(models.Model):
    post = models.ForeignKey(BlogPost, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Review by {self.author.username} for {self.post.title}"
