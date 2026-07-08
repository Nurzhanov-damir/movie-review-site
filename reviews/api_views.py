from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie, Critic, Review
from .serializers import (
    MovieSerializer,
    CriticSerializer,
    ReviewSerializer,
)


# ---------------------------------------------------------------------------
# Function-Based Views with DRF decorators (>=2 required)
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def movie_list_api(request):
    """List movies with optional filtering: ?genre=<id>&min_rating=<n>&search=<text>
    Also supports ?top_rated=1 to use the custom MovieManager.top_rated()."""
    if request.query_params.get('top_rated'):
        movies = Movie.objects.top_rated()
    else:
        movies = Movie.objects.all().select_related('genre')

    genre_id = request.query_params.get('genre')
    if genre_id:
        movies = movies.filter(genre_id=genre_id)

    min_rating = request.query_params.get('min_rating')
    if min_rating:
        movies = movies.filter(rating__gte=float(min_rating))

    search = request.query_params.get('search')
    if search:
        movies = movies.filter(Q(title__icontains=search) | Q(description__icontains=search))

    serializer = MovieSerializer(movies, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def critic_list_create_api(request):
    """GET: list all critics. POST: create a new critic (auth required)."""
    if request.method == 'GET':
        critics = Critic.objects.all()
        serializer = CriticSerializer(critics, many=True)
        return Response(serializer.data)

    serializer = CriticSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Class-Based Views via APIView (>=2 required).
# Together these two views implement full CRUD for the Review model.
# ---------------------------------------------------------------------------

class ReviewListCreateAPIView(APIView):
    """GET: list reviews (optionally filtered by ?movie=<id>).
    POST: create a review, linked to the authenticated user."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        reviews = Review.objects.select_related('user', 'movie').all()
        movie_id = request.query_params.get('movie')
        if movie_id:
            reviews = reviews.filter(movie_id=movie_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailAPIView(APIView):
    """GET/PUT/PATCH/DELETE for a single review. Only the review's author
    may update or delete it."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Review, pk=pk)

    def get(self, request, pk):
        review = self.get_object(pk)
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    def put(self, request, pk):
        review = self.get_object(pk)
        if review.user != request.user:
            return Response({'detail': 'Вы не можете редактировать чужой отзыв.'},
                             status=status.HTTP_403_FORBIDDEN)
        serializer = ReviewSerializer(review, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        review = self.get_object(pk)
        if review.user != request.user:
            return Response({'detail': 'Вы не можете редактировать чужой отзыв.'},
                             status=status.HTTP_403_FORBIDDEN)
        serializer = ReviewSerializer(review, data=request.data, partial=True,
                                       context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        review = self.get_object(pk)
        if review.user != request.user:
            return Response({'detail': 'Вы не можете удалить чужой отзыв.'},
                             status=status.HTTP_403_FORBIDDEN)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Token-based authentication: login / logout endpoints
# ---------------------------------------------------------------------------

class LoginAPIView(ObtainAuthToken):
    """POST {username, password} -> {token, user_id, username}"""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_api(request):
    """Deletes the requesting user's auth token, effectively logging them out."""
    Token.objects.filter(user=request.user).delete()
    return Response({'detail': 'Вы успешно вышли из системы.'}, status=status.HTTP_200_OK)
