from rest_framework import serializers
from .models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for Author model.
    """
    books_count = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Author
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'birth_date',
            'nationality',
            'biography',
            'books_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AuthorSimpleSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for Author model (for nested representations).
    """
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'full_name']


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for Book model.
    """
    authors = AuthorSimpleSerializer(many=True, read_only=True)
    author_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Author.objects.all(),
        source='authors'
    )
    authors_list = serializers.ReadOnlyField()

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'isbn',
            'publication_date',
            'genre',
            'pages',
            'price',
            'description',
            'authors',
            'author_ids',
            'authors_list',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_isbn(self, value):
        """
        Check that ISBN has correct length.
        """
        if len(value) not in [10, 13]:
            raise serializers.ValidationError(
                "ISBN must be either 10 or 13 characters long."
            )
        return value


class BookSimpleSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for Book model (for nested representations).
    """

    class Meta:
        model = Book
        fields = ['id', 'title', 'isbn', 'publication_date', 'genre', 'price']


class AuthorDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Author with their books.
    """
    books = BookSimpleSerializer(many=True, read_only=True)
    books_count = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Author
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'birth_date',
            'nationality',
            'biography',
            'books',
            'books_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']