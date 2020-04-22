from django.db import models
from django.urls import reverse


class Book(models.Model):
    """Book details"""
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
        """Return list of Author objects who wrote this book"""
        return Author.objects.filter(books = self)

    def get_absolute_url(self):
        """Return url for book detail page"""
        return reverse('book_detail', args=[str(self.book_id)])

    def __str__(self):
        return f'{self.title}'


class Author(models.Model):
    """Author details"""
    author_id = models.CharField(max_length=10, primary_key=True)
    given_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    books = models.ManyToManyField('Book', blank=True)

    def get_books(self):
        """Return list of Book objects written by this author"""
        return Book.objects.filter(authors = self)

    def __str__(self):
        return f'{self.surname}, {self.given_name}'