from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from rest_framework import generics, permissions, renderers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import OnixFile
from .serializers import OnixSerializer

# Create your views here.
def index(request):
    return render(request, 'index.html')

def view_book_detail(request):
    return render(request, 'book_detail.html')

@api_view(['POST'])
def submit_onix(request):
    serializer = OnixSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def process_onix(request):
    #read data from hard-coded file location
    #use lxml to parse the onix data into a series of Book objects
    #foreach Book object, see if it's in the database
    #   if so update it
    #   else add it
