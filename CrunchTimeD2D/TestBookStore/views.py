from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

# Create your views here.
def index(request):
    return render(request, 'index.html')

def view_book_detail(request):
    return render(request, 'book_detail.html')
