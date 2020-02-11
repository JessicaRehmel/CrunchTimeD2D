from django.db import models
from django.urls import reverse




class Book(models.Model):
    bookId = models.CharField(max_length=20)
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

    def get_authors(self):
        return Author.objects.filter(books = self)

    def get_absolute_url(self):
        return reverse('book_detail', args=[str(self.bookId)])

    def __str__(self):
        return f'{self.title}'



class Author(models.Model):
    givenName = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    books = models.ManyToManyField('Book', blank=True)

    def get_books(self):
        return Book.objects.filter(authors = self)

    def __str__(self):
        return f'{self.surname}, {self.givenName}'