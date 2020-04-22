from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from lxml import etree

from rest_framework import generics, permissions, renderers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

import onixcheck, os, html
from .models import *
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

# Create your views here.
def index(request):
    """Go to book list page"""
    all_books = Book.objects.all().order_by('title')
    paginator = Paginator(all_books, 3)

    """ context = {
        'all_books': all_books,
    } """
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'index.html', {'page_obj': page_obj})


def view_book_detail(request, book_id):
    """Go to book detail page"""
    book = Book.objects.get(book_id=book_id)

    context = {
        'book': book,
    }
    return render(request, 'book_detail.html', context = context)


class SearchResultsView(generic.ListView):
    """Display results of search query"""
    model = Book
    template_name = 'search.html'
    paginate_by = 3

    def get_context_data(self, *args, **kwargs):
        """Return context data of search query"""
        context = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        cat = self.request.GET.get('cat')
        q_list = query.split()
        book_list = Book.objects.none()
        title_list = Book.objects.none()
        isbn_list = Book.objects.none()
        exact_list = Book.objects.none()
        banned = []

        full_q = ""
        for ql in q_list:
            full_q = full_q + ql
            full_q = full_q + " "
        full_q = full_q[:len(full_q) - 1]
        print(full_q)
        if cat == "title" or cat == "any":
            exact_list = Book.objects.filter(Q(title__icontains=full_q) | Q(subtitle__icontains = full_q)).order_by('title')
        if cat == "author" or cat == "any":
            print("check")
            author_list = Author.objects.none()
            surname_list = Author.objects.none()
            givenname_list = Author.objects.none()
            for ql in full_q:
                surname_list = handle_if_none(surname_list, Author.objects.filter(surname__icontains = ql))
                givenname_list = handle_if_none(givenname_list, Author.objects.filter(given_name__icontains = ql))
            if surname_list and givenname_list:
                for s_name in surname_list:
                    if s_name in givenname_list:
                        author_list = handle_if_none(author_list, s_name)
            for author in author_list:
                    exact_list = handle_if_none(exact_list, author.get_books().order_by('title'))
        if cat == "isbn" or cat == "any":
            exact_list = handle_if_none(exact_list, Book.objects.filter(Q(isbn_13__icontains = full_q)).order_by('title'))

        if len(q_list) > 1:
            banned = ["a", "the", "and", "an", "or", "on", "of", "in"]

        all_banned = 1
        for ql in q_list:
            if ql.lower() not in banned:
                allbanned = 0

        if all_banned == 0:
            for ql in q_list[:]:
                if ql.lower() in banned:
                    q_list.remove(ql)

        print(q_list)

        for ql in q_list:
            if cat == "author" or cat == "any":
                author_list = Author.objects.none()
                author_list = Author.objects.filter(surname__icontains = ql)
                author_list = handle_if_none(author_list, Author.objects.filter(given_name__icontains = ql))
            if cat == "title" or cat == "any":
                title_list = handle_if_none(title_list, Book.objects.filter(Q(title__icontains=ql) | Q(subtitle__icontains = ql) | Q(series_name__icontains = ql)).order_by('title'))
            if cat == "author" or cat == "any":
                for a in author_list:
                    book_list = handle_if_none(book_list, a.get_books().order_by('title'))
                    # if book_list is None:
                    #     book_list = a.get_books().order_by('title')
                    # else:
                    #     book_list = book_list | a.get_books().order_by('title')

        if cat == "isbn" or cat == "any":
            temp = ""
            for digit in full_q:
                if digit.isdigit():
                    temp = temp + digit
            full_q = temp
            numeral_count = len(full_q)
            if numeral_count == 10:
                full_q = convert_to_isbn_13(full_q)     
                
            for num in range(numeral_count-1,numeral_count - 3, -1):
                for book in Book.objects.all():
                    similarity = 0
                    digit_count = 0
                    if len(book.isbn_13) == len(full_q):
                        for digit in book.isbn_13:
                            if digit == full_q[digit_count]:
                                similarity = similarity + 1
                            digit_count = digit_count + 1
                        if similarity == num:
                            isbn_list = handle_if_none(isbn_list, Book.objects.filter(isbn_13 = book.isbn_13))
                    elif len(book.isbn_13) == 10:
                        new_isbn = convert_to_isbn_13(book.isbn_13)
                        for digit in new_isbn:
                            if digit == full_q[digit_count]:
                                similarity = similarity + 1
                            digit_count = digit_count + 1
                        if similarity == num:
                            isbn_list = handle_if_none(isbn_list, Book.objects.filter(isbn_13 = new_isbn))
        
        #remove duplicates
        exact_list = list(dict.fromkeys(exact_list))
        if cat == "author" or cat == "any":
            book_list = list(dict.fromkeys(book_list)) 
        if cat == "title" or cat == "any":
            title_list = list(dict.fromkeys(title_list))
        if cat == "isbn" or cat == "any":
            isbn_list = list(dict.fromkeys(isbn_list))

        full_list = exact_list
        if cat == "author" or cat == "any":
            for i in book_list:
                full_list.append(i)
        if cat == "title" or cat == "any":
            for i in title_list:
                full_list.append(i)
        if cat == "isbn" or cat == "any":
            for i in isbn_list:
                full_list.append(i)
        full_list = list(dict.fromkeys(full_list))

        paginator = Paginator(full_list, self.paginate_by)
        page = self.request.GET.get('page')
        
        try:
            page_list = paginator.page(page)
        except PageNotAnInteger:
            page_list = paginator.page(1)
        except EmptyPage:
            page_list = paginator.page(paginator.num_pages)

        #create context
        context['full_list'] = page_list
        context['qu'] = query
        context['cat'] = cat
        context['page_obj'] = page_list
        return context



@api_view(['POST'])
def submit_onix(request):
    """Accept API Post with Onix book data, store in file"""
    f = open("tempOnix.xml", "wb")
    f.write(request.POST['data'].encode("utf-8"))
    f.close()
    try:
        errors = onixcheck.validate("tempOnix.xml")
        if (len(errors) == 0):
            f = open("onix.xml", "wb")
            f.write(request.POST['data'].encode("utf-8"))
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
    """Accept API Post to process stored Onix file"""
    with open("onix.xml", "rb") as f:
        xml = f.read()

    root = etree.fromstring(xml)
    ns = {}
    try:
        ns = {"onix": root.tag[1:len(root.tag) - len("ONIXMessage") - 1]}
    except:
        ns = {}

    book_list = []
    products = root.xpath("//onix:Product", namespaces = ns)
    for p in products:
        book = Book()

        #info from direct children of the product object
        book.book_id = p.xpath("./onix:RecordReference[1]", namespaces = ns)[0].text[24:]
        book.isbn_13 = p.xpath("./onix:ProductIdentifier[onix:ProductIDType='15']/onix:IDValue", namespaces = ns)[0].text

        #info from DescriptiveDetail child of product object
        book.title = unescape(p.xpath("./onix:DescriptiveDetail/onix:TitleDetail[onix:TitleType='01']/onix:TitleElement/onix:TitleText", namespaces = ns)[0].text)
        try:
            book.subtitle = unescape(p.xpath("./onix:DescriptiveDetail/onix:TitleDetail[onix:TitleType='01']/onix:TitleElement/onix:Subtitle", namespaces = ns)[0].text)
        except:
            book.subtitle = "N/A"
        try:
            book.series_name = unescape(p.xpath("./onix:DescriptiveDetail/onix:Collection/onix:TitleDetail[onix:TitleType='01']/onix:TitleElement[onix:TitleElementLevel='02']/onix:TitleText", namespaces = ns)[0].text)
        except:
            book.series_name = "N/A"
        try:
            book.volume_no = p.xpath("./onix:DescriptiveDetail/onix:Collection/onix:TitleDetail[onix:TitleType='01']/onix:TitleElement[onix:TitleElementLevel='01']/onix:PartNumber", namespaces = ns)[0].text
        except:
            book.volume_no = "N/A"
        book.book_format = p.xpath("./onix:DescriptiveDetail/onix:ProductFormDetail", namespaces = ns)[0].text    

        #info from CollateralDetail child of product object
        try:
            book.description = unescape(p.xpath("./onix:CollateralDetail/onix:TextContent[onix:TextType='03']/onix:Text", namespaces = ns)[0].text)
        except:
            book.description = "N/A"

        #info from PublishingDetail child of product object
        book.publisher = p.xpath("./onix:PublishingDetail/onix:Publisher[onix:PublishingRole='01']/onix:PublisherName", namespaces = ns)[0].text

        #info from ProductSupply child of product object
        try:
            release_date = p.xpath("./onix:ProductSupply/onix:MarketPublishingDetail/onix:MarketDate/onix:Date", namespaces = ns)[0].text #this is a string in YYYYMMDD format and may or may not need conversion?
            book.release_date = release_date[0:4] + '-' + release_date[4:6] + '-' + release_date[6:] + ' 00:00:00.000+00:00'
        except:
            book.release_date = "0000-01-01 00:00"
        book.price = p.xpath("./onix:ProductSupply/onix:SupplyDetail/onix:Price[onix:CurrencyCode='USD']/onix:PriceAmount", namespaces = ns)[0].text #I don't feel right about this line, but I can't articulate WHY - Jennifer      

        #save book
        book.save()
        
        #authors
        contribs = p.xpath("./onix:DescriptiveDetail/onix:Contributor", namespaces = ns)
        for a in book.authors.all():
            a.books.remove(book)
            book.authors.remove(a)

        for c in contribs:
            author = Author()
            
            author.author_id = c.xpath("./onix:PersonName", namespaces = ns)[0].text
            author.given_name = unescape(author.author_id.split()[0])
            try:
                author.surname = unescape(author.author_id.split()[1])
            except:
                author.surname = author.given_name
                author.given_name = ""

            author.save()
            book.authors.add(author)
            author.books.add(book)
    return Response("", status=status.HTTP_201_CREATED)


def unescape(hstr):
    """Translate HTML escape sequences"""
    pstr = ""
    delay = 0
    for i in range(0, 2):
        pstr = ""
        for i in range(0, len(hstr)):
            if delay == 0:
                try:
                    if hstr[i] == '&':
                        if hstr[i:i+4] == "&lt;":
                            pstr += "<"
                            delay = 3
                        elif hstr[i:i+4] == "&gt;":
                            pstr += ">"
                            delay = 3
                        elif hstr[i:i+5] == "&amp;":
                            pstr += "&"
                            delay = 4
                        elif hstr[i:i+6] == "&quot;":
                            pstr += '"'
                            delay = 5
                        elif hstr[i:i+6] == "&apos;":
                            pstr += "'"
                            delay = 5
                        elif hstr[i:i+2] == "&#":
                            pstr += chr(int(hstr[i+2:i+6]))
                            delay = 6
                        else:
                            pstr += hstr[i]
                    else:
                        pstr += hstr[i]
                except:
                    pstr += str(hstr[i])
            else:
                delay -= 1
        hstr = pstr
    return pstr


def convert_to_isbn_13(isbn_10):
    """Convert ISBN10 or ISBN13 to ISBN13"""
    isbn_13 = "978"
    for digit in isbn_10[:9]:
        isbn_13 = isbn_13 + digit

    check = 0
    for index in range(0, 10):
        if index % 2 == 1:
            check  = check + (int(isbn_10[index]) *  1)
        else:
            check  = check + (int(isbn_10[index]) *  3)
    check = check % 10

    if check != 0:
        check = 10 - check
    isbn_13 = isbn_13 + str(check)

    return isbn_13


def handle_if_none(list, query):
    """Handle empty queries"""
    if list is None:
        list = query
    else:
        list = list | query

    return list