from django.db import models
from django.urls import reverse


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

    def get_authors(self):
        return Author.objects.filter(books = self)

    def get_absolute_url(self):
        return reverse('book_detail', args=[str(self.bookId)])

    def __str__(self):
        return f'{self.title}'


class Author(models.Model):
    author_id = models.CharField(max_length=10, primary_key=True)
    given_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    books = models.ManyToManyField('Book', blank=True)

    def get_books(self):
        return Book.objects.filter(authors = self)

    def __str__(self):
        return f'{self.surname}, {self.givenName}'