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

# Create your views here.
def index(request):
    all_books = Book.objects.all().order_by('title')
    #all_books = Book.objects.filter(title__contains = "the")
    #all_books = Book.objects.filter(author__in = Author.objects.filter(surname__contains = "Arisoa")) | Book.objects.filter(author__in = Author.objects.filter(givenName = "Arisoa"))

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

class SearchResultsView(generic.ListView):
    model = Book
    template_name = 'search.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        author_list = Author.objects.filter(surname__icontains = query)
        author_list = author_list | Author.objects.filter(givenName__icontains = query)
        title_list = Book.objects.filter(Q(title__icontains=query) | Q(subtitle__icontains = query)).order_by('title')
        #subtitle_list = Book.objects.filter(subtitle__icontains = query).order_by('title')
        #title_list = title_list.union(subtitle_list, all = False)
        book_list = Book.objects.none()
        # add query authors
        for a in author_list:
            book_list = book_list.union(a.get_books(), all = False).order_by('title')
        desc_list = Book.objects.filter(description__icontains = query).order_by('title')
        context['author_list'] = book_list
        context['title_list'] = title_list
        context['desc_list'] = desc_list
        context['q'] = query
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        author_list = Author.objects.filter(surname__icontains = query)
        author_list = author_list | Author.objects.filter(givenName__icontains = query)
        title_list = Book.objects.filter(title__icontains=query)
        subtitle_list = Book.objects.filter(subtitle__icontains = query)
        book_list = Book.objects.none()
        # add query authors
        for a in author_list:
            book_list = book_list.union(a.get_books(), all = False)
        #add query titles
        #book_list = book_list.union(title_list, all = False)
        # add query subtitles
        #book_list = book_list.union(subtitle_list, all = False)
        # add descriptions
        desc_list = Book.objects.filter(description__icontains = query)
        #book_list = book_list.union(desc_list, all = False)
        t = book_list
        return t



@api_view(['POST'])
def submit_onix(request):
    f = open("tempOnix.xml", "w")
    f.write(request.POST['data'])
    f.close()
    try:
        errors = onixcheck.validate("tempOnix.xml")
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
