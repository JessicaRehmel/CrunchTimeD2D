from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from lxml import etree

from rest_framework import generics, permissions, renderers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import OnixFile, Book, Author
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
    with open("onix.xml") as f:
        xml = f.read()

    root = etree.fromstring(xml)

    book_list = []
    products = root.xpath("//Product")
    for p in products:
        book = Book()

        #info from direct children of the product object
        book.bookId = p.xpath("./RecordReference[1]")[0].text
        book.isbn13 = p.xpath("./ProductIdentifier[ProductIDType='15']/IDValue")[0].text

        #info from DescriptiveDetail child of product object
        book.title = p.xpath("./DescriptiveDetail/TitleDetail[TitleType='01']/TitleElement/TitleText")[0].text
        book.subtitle = p.xpath("./DescriptiveDetail/TitleDetail[TitleType='01']/TitleElement/Subtitle")[0].text
        book.seriesName = p.xpath("./DescriptiveDetail/Collection/TitleDetail[TitleType='01']/TitleElement[TitleElementLevel='02']/TitleText")[0].text
        book.volumeNo = p.xpath("./DescriptiveDetail/Collection/TitleDetail[TitleType='01']/TitleElement[TitleElementLevel='01']/PartNumber")[0].text
        book.bookFormat = p.xpath("./DescriptiveDetail/ProductFormDetail")[0].text #ProductFormDetail E101 indicates EPUB
        #TODO: figure out how to get/handle authors with given name & surname

        #info from CollateralDetail child of product object
        book.description = p.xpath("")[0].text

        #info from PublishingDetail child of product object
        book.publisher = p.xpath("")[0].text

        #info from ProductSupply child of product object
        book.price = p.xpath("")[0].text
        book.releaseDate = p.xpath("")[0].text           

        #add the book to the list
        book_list.append(book)
    
    #foreach Book b in book_list, see if it's in the database
    #   foreach Author in b.authors, see if it's in the database
    #       if so update author
    #       else add author
    #   if so update book
    #   else add book
