from django.urls import path

from . import api_views

urlpatterns = [
    path('movies/', api_views.movie_list_api, name='api_movie_list'),
    path('critics/', api_views.critic_list_create_api, name='api_critic_list_create'),

    path('reviews/', api_views.ReviewListCreateAPIView.as_view(), name='api_review_list_create'),
    path('reviews/<int:pk>/', api_views.ReviewDetailAPIView.as_view(), name='api_review_detail'),

    path('login/', api_views.LoginAPIView.as_view(), name='api_login'),
    path('logout/', api_views.logout_api, name='api_logout'),
]
