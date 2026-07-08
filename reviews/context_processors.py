from .models import Genre


def genres_processor(request):
    return {
        'nav_genres': Genre.objects.all(),
    }
