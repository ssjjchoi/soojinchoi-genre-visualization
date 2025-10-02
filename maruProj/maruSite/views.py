from django.shortcuts import render
import time

# Create your views here.
def index(request):
    current_time = int(time.time())
    context = {
        'timestamp_genre': current_time, 
        'timestamp_price': current_time + 1,
    }
    return render(request, 'maru/index.html', context)

def location(request):
    return render(request, 'maru/location.html')

def genre(request):
    return render(request, 'maru/genre.html')