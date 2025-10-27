from django.db.models import Count, Avg, Q
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django_filters.rest_framework import DjangoFilterBackend

from .models import Author, Book
from .serializers import (
    AuthorSerializer,
    AuthorDetailSerializer,
    BookSerializer
)


@api_view(['GET'])
def api_root(view, request, format=None):
    """
    API Root - Welcome to Bookshop API

    This API provides endpoints for managing books and authors.
    """
    return Response({
        'message': 'Welcome to Bookshop API! 📚',
        'version': '1.0.0',
        'endpoints': {
            'authors': reverse('author-list', request=request, format=format),
            'books': reverse('book-list', request=request, format=format),
        },
        'documentation': {
            'swagger': 'Coming soon',
            'github': 'https://github.com/Antonella94duarte/bookshop',
        },
        'features': [
            'Full CRUD operations',
            'Advanced filtering and search',
            'Pagination support',
            'Comprehensive statistics',
            'Docker containerization',
        ]
    })

class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows authors to be viewed or edited.

    Provides:
    - list: Get all authors
    - retrieve: Get a specific author
    - create: Create a new author
    - update: Update an author
    - partial_update: Partially update an author
    - destroy: Delete an author
    - with_books: Get authors with their book count (custom action)
    - top_authors: Get authors with most books (custom action)
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nationality']
    search_fields = ['first_name', 'last_name', 'biography']
    ordering_fields = ['last_name', 'first_name', 'birth_date', 'created_at']
    ordering = ['last_name', 'first_name']

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        """
        if self.action == 'retrieve':
            return AuthorDetailSerializer
        return AuthorSerializer

    @action(detail=False, methods=['get'])
    def with_books(self, request):
        """
        Get all authors with their book count.
        Demonstrates use of annotate.
        """
        authors = Author.objects.annotate(
            total_books=Count('books')
        ).order_by('-total_books')

        serializer = self.get_serializer(authors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_authors(self, request):
        """
        Get top 5 authors with most books.
        Demonstrates use of annotate and complex queries.
        """
        limit = int(request.query_params.get('limit', 5))

        authors = Author.objects.annotate(
            total_books=Count('books')
        ).filter(
            total_books__gt=0
        ).order_by('-total_books')[:limit]

        data = []
        for author in authors:
            data.append({
                'id': author.id,
                'full_name': author.full_name,
                'nationality': author.nationality,
                'total_books': author.total_books
            })

        return Response(data)

    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        """
        Get all books by a specific author.
        """
        author = self.get_object()
        books = author.books.all()

        from .serializers import BookSimpleSerializer
        serializer = BookSimpleSerializer(books, many=True)
        return Response(serializer.data)


class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows books to be viewed or edited.

    Provides:
    - list: Get all books
    - retrieve: Get a specific book
    - create: Create a new book
    - update: Update a book
    - partial_update: Partially update a book
    - destroy: Delete a book
    - by_genre: Get books filtered by genre (custom action)
    - statistics: Get book statistics (custom action)
    - search_books: Advanced search (custom action)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre', 'authors']
    search_fields = ['title', 'isbn', 'description']
    ordering_fields = ['title', 'publication_date', 'price', 'pages', 'created_at']
    ordering = ['-publication_date', 'title']

    def get_queryset(self):
        """
        Optionally restricts the returned books by filtering against
        query parameters in the URL.
        """
        queryset = Book.objects.all()

        # Filter by minimum price
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        # Filter by maximum price
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(publication_date__year=year)

        return queryset

    @action(detail=False, methods=['get'])
    def by_genre(self, request):
        """
        Get books grouped by genre with count.
        Demonstrates use of values and annotate.
        """
        genre_stats = Book.objects.values('genre').annotate(
            count=Count('id'),
            avg_price=Avg('price')
        ).order_by('-count')

        return Response(genre_stats)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get overall book statistics.
        Demonstrates use of aggregate.
        """
        from django.db.models import Sum, Max, Min

        stats = Book.objects.aggregate(
            total_books=Count('id'),
            avg_price=Avg('price'),
            max_price=Max('price'),
            min_price=Min('price'),
            avg_pages=Avg('pages'),
            total_authors=Count('authors', distinct=True)
        )

        # Add genre distribution
        genre_distribution = list(
            Book.objects.values('genre').annotate(
                count=Count('id')
            ).order_by('-count')
        )

        stats['genre_distribution'] = genre_distribution

        return Response(stats)

    @action(detail=False, methods=['get'])
    def search_books(self, request):
        """
        Advanced search with multiple filters.
        Demonstrates complex queries with Q objects.
        """
        query = request.query_params.get('q', '')
        genre = request.query_params.get('genre', '')
        author_name = request.query_params.get('author', '')

        books = Book.objects.all()

        # Search in title, description, or ISBN
        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(isbn__icontains=query)
            )

        # Filter by genre
        if genre:
            books = books.filter(genre=genre)

        # Filter by author name
        if author_name:
            books = books.filter(
                Q(authors__first_name__icontains=author_name) |
                Q(authors__last_name__icontains=author_name)
            ).distinct()

        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_author(self, request, pk=None):
        """
        Add an author to a book.
        """
        book = self.get_object()
        author_id = request.data.get('author_id')

        if not author_id:
            return Response(
                {'error': 'author_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            author = Author.objects.get(id=author_id)
            book.authors.add(author)
            serializer = self.get_serializer(book)
            return Response(serializer.data)
        except Author.DoesNotExist:
            return Response(
                {'error': 'Author not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_author(self, request, pk=None):
        """
        Remove an author from a book.
        """
        book = self.get_object()
        author_id = request.data.get('author_id')

        if not author_id:
            return Response(
                {'error': 'author_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            author = Author.objects.get(id=author_id)
            book.authors.remove(author)
            serializer = self.get_serializer(book)
            return Response(serializer.data)
        except Author.DoesNotExist:
            return Response(
                {'error': 'Author not found'},
                status=status.HTTP_404_NOT_FOUND
            )