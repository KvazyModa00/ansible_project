from django.shortcuts import render
from .models import FIO, Job

def index(request):
    fios = FIO.objects.all()
    jobs = Job.objects.all()
    return render(request, 'index.html', {'fios': fios, 'jobs': jobs})