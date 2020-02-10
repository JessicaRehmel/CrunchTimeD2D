from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from rest_framework import generics, permissions, renderers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import *

from .models import OnixFile
from .serializers import OnixSerializer

# Create your views here.
def index(request):
    all_books = Book.objects.all()

    context = {
        'all_books': all_books,
    }
    return render(request, 'index.html', context = context)

def view_book_detail(request, ID):
    book = Book.objects.get(bookId=ID)

    context = {
        'book': book,
    }
    return render(request, 'book_detail.html', context = context)

@api_view(['POST'])
def submit_onix(request):
    serializer = OnixSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)