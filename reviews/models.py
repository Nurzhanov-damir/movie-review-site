from django.db import models
from django.contrib.auth.models import User


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Critic(models.Model):
    name = models.CharField(max_length=150)
    publication = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.name


class MovieManager(models.Manager):
    def top_rated(self):
        return self.filter(rating__gte=8.0)


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_year = models.IntegerField()
    box_office = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rating = models.FloatField(default=0)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='movies')
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)

    objects = MovieManager()

    def __str__(self):
        return self.title


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_reviews', blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"

    def likes_count(self):
        return self.likes.count()