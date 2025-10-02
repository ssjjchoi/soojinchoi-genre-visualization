from . import views, viewsOfIndex
from django.urls import path

urlpatterns = [
    # index 페이지에서 사용
    path('index/genre_chart/', viewsOfIndex.genre_chart, name='genre-chart'),
    path('index/price_chart/', viewsOfIndex.price_by_location_chart, name='price-chart'),

    # genre 페이지에서 사용

    # location 페이지에서 사용
]
