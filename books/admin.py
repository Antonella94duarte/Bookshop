from django.contrib import admin
from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'nationality', 'birth_date', 'books_count', 'created_at']
    list_filter = ['nationality', 'created_at']
    search_fields = ['first_name', 'last_name', 'biography']
    date_hierarchy = 'birth_date'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'birth_date', 'nationality')
        }),
        ('Biography', {
            'fields': ('biography',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'isbn', 'genre', 'publication_date', 'pages', 'price', 'created_at']
    list_filter = ['genre', 'publication_date', 'authors']
    search_fields = ['title', 'isbn', 'description']
    date_hierarchy = 'publication_date'
    filter_horizontal = ['authors']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'isbn', 'authors')
        }),
        ('Publication Details', {
            'fields': ('publication_date', 'genre', 'pages', 'price')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )