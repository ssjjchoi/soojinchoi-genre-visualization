from . import views
from django.urls import path

app_name = 'maru'
urlpatterns = [
    path('', views.index, name='index'),
    path('location/', views.location, name='location'),
    path('genre/', views.genre, name='genre'),
]
