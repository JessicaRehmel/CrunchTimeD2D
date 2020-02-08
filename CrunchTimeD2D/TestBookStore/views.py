from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from lxml import etree

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
    with open("onix.xml") as f:
        xml = f.read()

    root = etree.fromstring(xml)

    book_dict = {} #used to store the data about a book until it goes into the database
    books = [] #holds all the book_dict objects

    for obj in root.getchildren(): #gets the header & all products
        if obj.tag == "Product": #filters out anything that isn't a book
            for elem in obj.getchildren(): #gets all the elements describing the current book
                if not elem.text:
                    text = "None"
                else:
                    text = elem.text

                if elem.tag == "RecordReference":
                    book_dict[elem.tag] = text
                '''if/elif/else switch to collect all the relevant data about the current book:
                --bookId
                --isbn13
                --title
                --subtitle
                --seriesName
                --volumeNo
                --authors                                
                    --givenName
                    --surname
                --description
                --bookFormat
                --price
                --releaseDate
                '''

    
    #foreach Book object, see if it's in the database
    #   foreach Author object, see if it's in the database
    #       if so update it
    #       else add it
    #   if so update it
    #   else add it
