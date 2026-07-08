from rest_framework import serializers

from .models import Genre, Critic, Movie, Review


# ---------------------------------------------------------------------------
# ModelSerializer-based serializers (>=2 required)
# ---------------------------------------------------------------------------

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class MovieSerializer(serializers.ModelSerializer):
    genre_name = serializers.ReadOnlyField(source='genre.name')
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'description', 'release_year', 'box_office',
            'rating', 'genre', 'genre_name', 'poster', 'reviews_count',
        ]

    def get_reviews_count(self, obj):
        return obj.reviews.count()


# ---------------------------------------------------------------------------
# Plain Serializer-based serializers (>=2 required) — fields and
# create()/update() are declared and validated manually.
# ---------------------------------------------------------------------------

class ReviewSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    movie = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all())
    movie_title = serializers.ReadOnlyField(source='movie.title')
    user = serializers.ReadOnlyField(source='user.username')
    text = serializers.CharField()
    score = serializers.IntegerField()
    created_at = serializers.DateTimeField(read_only=True)
    likes_count = serializers.SerializerMethodField()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def validate_score(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError('Оценка должна быть от 1 до 10.')
        return value

    def validate_text(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Текст отзыва слишком короткий.')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return Review.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.score = validated_data.get('score', instance.score)
        instance.movie = validated_data.get('movie', instance.movie)
        instance.save()
        return instance


class CriticSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=150)
    publication = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('Имя критика не может быть пустым.')
        return value.strip()

    def create(self, validated_data):
        return Critic.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.publication = validated_data.get('publication', instance.publication)
        instance.save()
        return instance
