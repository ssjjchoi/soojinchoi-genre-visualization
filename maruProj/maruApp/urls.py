from . import views, viewsOfIndex, viewsOfJenre
from django.urls import path

urlpatterns = [
    # index 페이지에서 사용
    path('index/genre_chart/', viewsOfIndex.genre_chart, name='genre-chart'),
    path('index/price_chart/', viewsOfIndex.price_by_location_chart, name='price-chart'),

    # genre 페이지에서 사용
    path('genre/', viewsOfJenre.genre_page, name='genre'),
    path('genre/data/', viewsOfJenre.genre_data, name='genre-data'),
    path('genre/gmv-data/', viewsOfJenre.genre_gmv_data, name='genre-gmv-data'),
    path('genre/top3/', viewsOfJenre.genre_top3_json, name='genre-top3-json'),
    path('genre/price-data/', viewsOfJenre.genre_price_data, name='genre-price-data'),
    path('genre/recommend-top3/', viewsOfJenre.genre_recommend_top3, name='genre-recommend-top3'),
    path('genre/heatmap/', viewsOfJenre.genre_heatmap, name='genre-heatmap'),

    # location 페이지에서 사용
]
