from django.test import TestCase
from django.contrib.auth.models import User
from .models import Author, Genre, Book, Customer

class BookModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(GenreName='Fiction')
        self.author = Author.objects.create(
            FirstName='Test',
            LastName='Author',
            Bio='Test bio'
        )
        
    def test_book_creation(self):
        book = Book.objects.create(
            Title='Test Book',
            AuthorID=self.author,
            GenreID=self.genre,
            ISBN='1234567890',
            PublicationDate='2023-01-01',
            Price=19.99,
            Stock=10
        )
        self.assertEqual(book.Title, 'Test Book')
        self.assertEqual(book.is_available, True)