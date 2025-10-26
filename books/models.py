from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Author(models.Model):
    """
    Author model representing book authors.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    biography = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def books_count(self):
        return self.books.count()


class Book(models.Model):
    """
    Book model representing books in the bookshop.
    """
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('fantasy', 'Fantasy'),
        ('mystery', 'Mystery'),
        ('romance', 'Romance'),
        ('thriller', 'Thriller'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    publication_date = models.DateField()
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='other')
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    description = models.TextField(blank=True)
    authors = models.ManyToManyField(Author, related_name='books')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publication_date', 'title']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['publication_date']),
            models.Index(fields=['genre']),
        ]

    def __str__(self):
        return self.title

    @property
    def authors_list(self):
        return ", ".join([author.full_name for author in self.authors.all()])