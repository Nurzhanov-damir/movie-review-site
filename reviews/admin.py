from django.contrib import admin
from .models import Genre, Critic, Movie, Review

admin.site.register(Genre)
admin.site.register(Critic)
admin.site.register(Movie)
admin.site.register(Review)