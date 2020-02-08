from django.db import models
from django.urls import reverse


class OnixFile(models.Model):
    data = models.TextField()



class Book(models.Model):
    bookId = models.CharField(max_length=100)
    isbn13 = models.CharField(max_length=20)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, blank=True)
    seriesName = models.CharField(max_length=100, blank=True)
    volumeNo = models.CharField(max_length=3, blank=True)
    authors = models.ManyToManyField('Author', blank=True)
    description = models.TextField(blank=True)
    bookFormat = models.CharField(max_length=10)
    price = models.CharField(max_length=10)
    releaseDate = models.DateTimeField()
    publisher = models.CharField(max_length=100, blank=True)



class Author(models.Model):
    givenName = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    books = models.ManyToManyField('Book', blank=True)
