from django.db import models
from django.urls import reverse


class OnixFile(models.Model):
    data = models.TextField()



class Book(models.Model):
    book_id = models.CharField(max_length=100, primary_key=True)
    isbn_13 = models.CharField(max_length=20)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, blank=True)
    series_name = models.CharField(max_length=100, blank=True)
    volume_no = models.CharField(max_length=3, blank=True)
    authors = models.ManyToManyField('Author', blank=True)
    description = models.TextField(blank=True)
    book_format = models.CharField(max_length=10, blank=True)
    price = models.CharField(max_length=10, blank=True)
    release_date = models.DateTimeField(blank=True)
    publisher = models.CharField(max_length=100, blank=True)



class Author(models.Model):
    author_id = models.CharField(max_length=10, primary_key=True)
    given_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    books = models.ManyToManyField('Book', blank=True)
