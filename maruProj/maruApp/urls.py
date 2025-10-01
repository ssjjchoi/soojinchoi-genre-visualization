from . import views
from django.urls import path

urlpatterns = [
    path('book_chart/', views.book_chart, name='book-chart'),
]
