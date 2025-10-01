from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'maru/index.html')

def location(request):
    return render(request, 'maru/location.html')

def genre(request):
    return render(request, 'maru/genre.html')