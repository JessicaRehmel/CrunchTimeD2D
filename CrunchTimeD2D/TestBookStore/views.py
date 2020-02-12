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
        qlist = query.split()
        book_list = Book.objects.none()
        title_list = Book.objects.none()
        desc_list = Book.objects.none()

        author_list = Author.objects.filter(surname__icontains = qlist[0])
        if author_list is None:
            author_list = Author.objects.filter(givenName__icontains = qlist[0])
        else:
            author_list = author_list | Author.objects.filter(givenName__icontains = qlist[0])
        title_list = Book.objects.filter(Q(title__icontains=qlist[0]) | Q(subtitle__icontains = qlist[0])).order_by('title')
        #subtitle_list = Book.objects.filter(subtitle__icontains = query).order_by('title')
        #title_list = title_list.union(subtitle_list, all = False)
        # add query authors
        for a in author_list:
            if book_list is None:
                book_list = a.get_books().order_by('title')
            else:    
                book_list = book_list | a.get_books().order_by('title')
        desc_list = Book.objects.filter(description__icontains = qlist[0]).order_by('title')


        print("BEFORE SECOND LOOP")
        for ql in qlist[1:]:
            print("AFTER SECOND LOOP")
            author_list = Author.objects.none()
            author_list = Author.objects.filter(surname__icontains = ql)
            #author_list = author_list | Author.objects.filter(surname__icontains = ql)
            print("CHECK1")
            if author_list is None:
                author_list = Author.objects.filter(givenName__icontains = ql)
            else:
                author_list = author_list | Author.objects.filter(givenName__icontains = ql)
            #author_list = author_list | Author.objects.filter(givenName__icontains = ql)
            print("CHECK2")
            if title_list is None:
                print("TITLE NONE")
                title_list = Book.objects.filter(Q(title__icontains=ql) | Q(subtitle__icontains = ql)).order_by('title')
            else:
                title_list = title_list | Book.objects.filter(Q(title__icontains=ql) | Q(subtitle__icontains = ql)).order_by('title')
            #subtitle_list = Book.objects.filter(subtitle__icontains = query).order_by('title')
            #title_list = title_list.union(subtitle_list, all = False)
            #book_list = Book.objects.none()
            # add query authors
            print("CHECK3")
            for a in author_list:
                print("CHECK3.5")
                print(book_list)
                if book_list is None:
                    print("BOOK NONE")
                    book_list = a.get_books().order_by('title')
                else:
                    print("AHDFJLKGJLSGLKDJLSD")
                    book_list = book_list | a.get_books().order_by('title')
            print("CHECK4")
            print(book_list)
            if desc_list is None:
                print("DESC NONE")
                desc_list = Book.objects.filter(description__icontains = ql).order_by('title')
            else:
                desc_list = desc_list | Book.objects.filter(description__icontains = ql).order_by('title')
            print("CHECK5")
        print("CHECKKKKKKK")
        print(book_list)
        print(title_list)
        print(desc_list)
        context['author_list'] = book_list
        context['title_list'] = title_list
        context['desc_list'] = desc_list
        context['q'] = query
        print("CHECK6")
        return context



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
