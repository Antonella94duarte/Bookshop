from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from datetime import date
from decimal import Decimal

from .models import Author, Book


class AuthorModelTest(TestCase):
    """Tests for the Author model."""

    def setUp(self):
        self.author = Author.objects.create(
            first_name="Gabriel",
            last_name="García Márquez",
            birth_date=date(1927, 3, 6),
            nationality="Colombian",
            biography="Nobel Prize winning author"
        )

    def test_author_creation(self):
        """Test author is created correctly."""
        self.assertEqual(self.author.first_name, "Gabriel")
        self.assertEqual(self.author.last_name, "García Márquez")
        self.assertEqual(self.author.full_name, "Gabriel García Márquez")

    def test_author_str(self):
        """Test author string representation."""
        self.assertEqual(str(self.author), "Gabriel García Márquez")

    def test_books_count_property(self):
        """Test books_count property."""
        self.assertEqual(self.author.books_count, 0)

        # Create a book
        book = Book.objects.create(
            title="One Hundred Years of Solitude",
            isbn="9780060883287",
            publication_date=date(1967, 5, 30),
            genre="fiction",
            pages=417,
            price=Decimal("15.99")
        )
        book.authors.add(self.author)

        self.assertEqual(self.author.books_count, 1)


class BookModelTest(TestCase):
    """Tests for the Book model."""

    def setUp(self):
        self.author = Author.objects.create(
            first_name="George",
            last_name="Orwell",
            birth_date=date(1903, 6, 25),
            nationality="British"
        )

        self.book = Book.objects.create(
            title="1984",
            isbn="9780451524935",
            publication_date=date(1949, 6, 8),
            genre="fiction",
            pages=328,
            price=Decimal("12.99"),
            description="A dystopian social science fiction novel"
        )
        self.book.authors.add(self.author)

    def test_book_creation(self):
        """Test book is created correctly."""
        self.assertEqual(self.book.title, "1984")
        self.assertEqual(self.book.isbn, "9780451524935")
        self.assertEqual(self.book.pages, 328)

    def test_book_str(self):
        """Test book string representation."""
        self.assertEqual(str(self.book), "1984")

    def test_authors_list_property(self):
        """Test authors_list property."""
        self.assertEqual(self.book.authors_list, "George Orwell")

        # Add another author
        author2 = Author.objects.create(
            first_name="Test",
            last_name="Author"
        )
        self.book.authors.add(author2)

        self.assertIn("George Orwell", self.book.authors_list)
        self.assertIn("Test Author", self.book.authors_list)


class AuthorAPITest(APITestCase):
    """Tests for the Author API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.author_data = {
            'first_name': 'Jane',
            'last_name': 'Austen',
            'birth_date': '1775-12-16',
            'nationality': 'British',
            'biography': 'English novelist'
        }
        self.author = Author.objects.create(**self.author_data)

    def test_get_all_authors(self):
        """Test retrieving all authors."""
        url = reverse('author-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_single_author(self):
        """Test retrieving a single author."""
        url = reverse('author-detail', kwargs={'pk': self.author.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Jane')
        self.assertEqual(response.data['last_name'], 'Austen')

    def test_create_author(self):
        """Test creating a new author."""
        url = reverse('author-list')
        data = {
            'first_name': 'Charles',
            'last_name': 'Dickens',
            'birth_date': '1812-02-07',
            'nationality': 'British'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 2)
        self.assertEqual(response.data['first_name'], 'Charles')

    def test_update_author(self):
        """Test updating an author."""
        url = reverse('author-detail', kwargs={'pk': self.author.id})
        data = {'biography': 'Updated biography'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.author.refresh_from_db()
        self.assertEqual(self.author.biography, 'Updated biography')

    def test_delete_author(self):
        """Test deleting an author."""
        url = reverse('author-detail', kwargs={'pk': self.author.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Author.objects.count(), 0)

    def test_top_authors_endpoint(self):
        """Test the top_authors custom endpoint."""
        # Create books for author
        book = Book.objects.create(
            title="Pride and Prejudice",
            isbn="9780141439518",
            publication_date=date(1813, 1, 28),
            genre="fiction",
            pages=279,
            price=Decimal("9.99")
        )
        book.authors.add(self.author)

        url = reverse('author-top-authors')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)


class BookAPITest(APITestCase):
    """Tests for the Book API endpoints."""

    def setUp(self):
        self.client = APIClient()

        self.author = Author.objects.create(
            first_name='J.K.',
            last_name='Rowling',
            birth_date=date(1965, 7, 31),
            nationality='British'
        )

        self.book = Book.objects.create(
            title="Harry Potter and the Philosopher's Stone",
            isbn="9780747532699",
            publication_date=date(1997, 6, 26),
            genre="fantasy",
            pages=223,
            price=Decimal("19.99"),
            description="First book in the Harry Potter series"
        )
        self.book.authors.add(self.author)

    def test_get_all_books(self):
        """Test retrieving all books."""
        url = reverse('book-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_single_book(self):
        """Test retrieving a single book."""
        url = reverse('book-detail', kwargs={'pk': self.book.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Harry Potter and the Philosopher's Stone")

    def test_create_book(self):
        """Test creating a new book."""
        url = reverse('book-list')
        data = {
            'title': 'New Book',
            'isbn': '9781234567890',
            'publication_date': '2023-01-01',
            'genre': 'fiction',
            'pages': 300,
            'price': '15.99',
            'author_ids': [self.author.id]
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_update_book(self):
        """Test updating a book."""
        url = reverse('book-detail', kwargs={'pk': self.book.id})
        data = {'price': '24.99'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.price, Decimal('24.99'))

    def test_delete_book(self):
        """Test deleting a book."""
        url = reverse('book-detail', kwargs={'pk': self.book.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)

    def test_filter_by_genre(self):
        """Test filtering books by genre."""
        url = reverse('book-list')
        response = self.client.get(url, {'genre': 'fantasy'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_books(self):
        """Test searching books."""
        url = reverse('book-list')
        response = self.client.get(url, {'search': 'Harry'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_statistics_endpoint(self):
        """Test the statistics custom endpoint."""
        url = reverse('book-statistics')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_books', response.data)
        self.assertIn('avg_price', response.data)
        self.assertEqual(response.data['total_books'], 1)

    def test_by_genre_endpoint(self):
        """Test the by_genre custom endpoint."""
        url = reverse('book-by-genre')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)