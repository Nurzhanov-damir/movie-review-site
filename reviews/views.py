from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Movie, Review
from .forms import ReviewForm, RegisterForm, MovieSearchForm, MovieFilterForm


def movie_list(request):
    movies = Movie.objects.all().select_related('genre')

    search_form = MovieSearchForm(request.GET or None)
    filter_form = MovieFilterForm(request.GET or None)

    if search_form.is_valid() and search_form.cleaned_data.get('query'):
        query = search_form.cleaned_data['query']
        movies = movies.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if filter_form.is_valid():
        genre = filter_form.cleaned_data.get('genre')
        min_rating = filter_form.cleaned_data.get('min_rating')
        if genre:
            movies = movies.filter(genre=genre)
        if min_rating:
            movies = movies.filter(rating__gte=float(min_rating))

    context = {
        'movies': movies,
        'search_form': search_form,
        'filter_form': filter_form,
    }
    return render(request, 'reviews/movie_list.html', context)


def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    reviews = movie.reviews.select_related('user').order_by('-created_at')
    review_form = ReviewForm()

    context = {
        'movie': movie,
        'reviews': reviews,
        'review_form': review_form,
    }
    return render(request, 'reviews/movie_detail.html', context)


@login_required
def add_review(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user
            review.save()
            messages.success(request, 'Ваш отзыв успешно добавлен!')
            return redirect('movie_detail', pk=movie.pk)

        messages.error(request, 'Не удалось сохранить отзыв. Проверьте введённые данные.')
        reviews = movie.reviews.select_related('user').order_by('-created_at')
        return render(request, 'reviews/movie_detail.html', {
            'movie': movie,
            'reviews': reviews,
            'review_form': form,
        })

    return redirect('movie_detail', pk=movie.pk)


@login_required
def like_review(request, pk):
    review = get_object_or_404(Review, pk=pk)

    if request.user in review.likes.all():
        review.likes.remove(request.user)
    else:
        review.likes.add(request.user)

    return redirect('movie_detail', pk=review.movie.pk)


def register(request):
    if request.user.is_authenticated:
        return redirect('movie_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}! Регистрация прошла успешно.')
            return redirect('movie_list')
        messages.error(request, 'Пожалуйста, исправьте ошибки в форме регистрации.')
    else:
        form = RegisterForm()

    return render(request, 'reviews/register.html', {'form': form})
