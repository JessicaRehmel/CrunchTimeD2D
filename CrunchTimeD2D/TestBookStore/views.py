from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from rest_framework import generics, permissions, renderers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
import onixcheck

from .models import OnixFile
from .serializers import OnixSerializer

# Create your views here.
def index(request):
    return render(request, 'index.html')

def view_book_detail(request):
    return render(request, 'book_detail.html')

@api_view(['POST'])
def submit_onix(request):
    print(request)
    #f = open("validateOnix.xml", "w")
    #f.write("" + request.data)
    #f.close()
    #errors = onixcheck("validateOnix.xml")
    #if (errors[0].short[0:5] != "ERROR"):
    #f = open("onix.xml", "w")
    #f.write(request.data)
    #f.close()
    #return Response("", status=status.HTTP_201_CREATED)
    #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
