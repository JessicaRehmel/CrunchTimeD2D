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
        book.bookFormat = p.xpath("./DescriptiveDetail/ProductFormDetail")[0].text

        #authors
        author_list = []
        contribs = p.xpath("./DescriptiveDetail/Contributor")
        for c in contribs:
            author = Author()

            author.authorId = c.xpath("./NameIdentifier[NameIDType='01']/IDValue")[0].text
            
            names = c.xpath("./PersonName")[0].text
            author.givenName = names.split()[0]
            author.surname = names.split()[1]

            author_list.append(author)
            
        book.authors = author_list            

        #info from CollateralDetail child of product object
        book.description = p.xpath("./CollateralDetail/TextContent[TextType='03']/Text")[0].text

        #info from PublishingDetail child of product object
        book.publisher = p.xpath("./PublishingDetail/Publisher[PublishingRole='01']/PublisherName")[0].text

        #info from ProductSupply child of product object
        book.releaseDate = p.xpath("./ProductSupply/MarketPublishingDetail/MarketDate/Date")[0].text #this is a string in YYYYMMDD format and may or may not need conversion?
        book.price = p.xpath("./ProductSupply/SupplyDetail/Price[CurrencyCode='USD']/PriceAmount")[0].text #I don't feel right about this line, but I can't articulate WHY - Jennifer         

        #add the book to the list
        book_list.append(book)
    

    for b in book_list:
        for a in b.authors:
            pass
            #if a is in the database, update it
            #else add it
        
        #if b is in the database, update it
        #else add it