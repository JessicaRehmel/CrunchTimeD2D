from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from rest_framework import generics, permissions, renderers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

import onixcheck, os
from .models import *
from django.db.models import Q

from .models import OnixFile
from .serializers import OnixSerializer

# Create your views here.
def index(request):
    all_books = Book.objects.all().order_by('title')
    #all_books = Book.objects.filter(title__contains = "the")
    #all_books = Book.objects.filter(author__in = Author.objects.filter(surname__contains = "Arisoa")) | Book.objects.filter(author__in = Author.objects.filter(givenName = "Arisoa"))

    context = {
        'all_books': all_books,
    }
    return render(request, 'index.html', context = context)

""" def search(request):
    all_books = Book.objects.all().order_by('title')
    #all_books = Book.objects.filter(title__contains = "the")
    all_books = Book.objects.filter(author__in = Author.objects.filter(surname__contains = "Arisoa")) | Book.objects.filter(author__in = Author.objects.filter(givenName = "Arisoa"))

    context = {
        'all_books': all_books,
    }
    return render(request, 'search.html', context = context) """

class SearchResultsView(generic.ListView):
    model = Book
    template_name = 'search.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = Book.objects.filter(
            Q(title__icontains='subject')
        )
        return object_list


def view_book_detail(request):
    return render(request, 'book_detail.html')

@api_view(['POST'])
def submit_onix(request):
    f = open("tempOnix.xml", "w")
    f.write(request.POST['data'])
    f.close()
    try:
        errors = onixcheck.validate("onix.xml")
        if (len(errors) == 0):
            f = open("onix.xml", "w")
            f.write(request.POST['data'])
            f.close()
            os.remove("tempOnix.xml")
            return Response("", status=status.HTTP_201_CREATED)
        os.remove("tempOnix.xml")
        return Response("Invalid ONIX", status=status.HTTP_400_BAD_REQUEST)
    except:
        os.remove("tempOnix.xml")
        return Response("Invalid XML", status=status.HTTP_400_BAD_REQUEST)
