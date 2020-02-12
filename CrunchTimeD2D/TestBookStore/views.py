from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from lxml import etree

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

    context = {
        'all_books': all_books,
    }
    return render(request, 'index.html', context = context)

def view_book_detail(request, book_id):
    book = Book.objects.get(book_id=book_id)

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
        banned = []

        if len(qlist) > 1:
            banned = ["a", "the", "and", "or", "an"]

        print(banned)

        author_list = Author.objects.filter(surname__icontains = qlist[0])
        if author_list is None:
            author_list = Author.objects.filter(given_name__icontains = qlist[0])
        else:
            author_list = author_list | Author.objects.filter(given_name__icontains = qlist[0])
        print(author_list)
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
                author_list = Author.objects.filter(given_name__icontains = ql)
            else:
                author_list = author_list | Author.objects.filter(given_name__icontains = ql)
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

@api_view(['POST'])
def process_onix(request):
    with open("onix.xml") as f:
        xml = f.read()

    root = etree.fromstring(xml)

    book_list = []
    products = root.xpath("//Product")
    for p in products:
        book = Book()

        #info from direct children of the product object
        book.book_id = p.xpath("./RecordReference[1]")[0].text
        book.isbn_13 = p.xpath("./ProductIdentifier[ProductIDType='15']/IDValue")[0].text

        #info from DescriptiveDetail child of product object
        book.title = p.xpath("./DescriptiveDetail/TitleDetail[TitleType='01']/TitleElement/TitleText")[0].text
        book.subtitle = p.xpath("./DescriptiveDetail/TitleDetail[TitleType='01']/TitleElement/Subtitle")[0].text
        book.series_name = p.xpath("./DescriptiveDetail/Collection/TitleDetail[TitleType='01']/TitleElement[TitleElementLevel='02']/TitleText")[0].text
        book.volume_no = p.xpath("./DescriptiveDetail/Collection/TitleDetail[TitleType='01']/TitleElement[TitleElementLevel='01']/PartNumber")[0].text
        book.book_format = p.xpath("./DescriptiveDetail/ProductFormDetail")[0].text

        #authors
        author_list = []
        contribs = p.xpath("./DescriptiveDetail/Contributor")
        for c in contribs:
            author = Author()

            author.author_id = c.xpath("./NameIdentifier[NameIDType='01']/IDValue")[0].text
            
            names = c.xpath("./PersonName")[0].text
            author.given_name = names.split()[0]
            author.surname = names.split()[1]

            author_list.append(author)
            
        book.authors = author_list            

        #info from CollateralDetail child of product object
        book.description = p.xpath("./CollateralDetail/TextContent[TextType='03']/Text")[0].text

        #info from PublishingDetail child of product object
        book.publisher = p.xpath("./PublishingDetail/Publisher[PublishingRole='01']/PublisherName")[0].text

        #info from ProductSupply child of product object
        book.release_date = p.xpath("./ProductSupply/MarketPublishingDetail/MarketDate/Date")[0].text #this is a string in YYYYMMDD format and may or may not need conversion?
        book.price = p.xpath("./ProductSupply/SupplyDetail/Price[CurrencyCode='USD']/PriceAmount")[0].text #I don't feel right about this line, but I can't articulate WHY - Jennifer         

        #add the book to the list
        book_list.append(book)
    

    for b in book_list:        
        b.save() #Django is smart; in theory, if it sees a book_id it already has then it should update and otherwise it should insert
        
        for a in b.authors:
            a.save() #ditto for author_id
            
            b.authors.add(a) #add it to the book
            a.books.add(b) #add the book to it
