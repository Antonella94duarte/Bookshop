from django.contrib import admin
from django.utils.html import format_html, mark_safe
from decimal import Decimal
from django.db.models import Count, Avg
from datetime import date
from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for Author model with custom fields and styling.
    """
    list_display = [
        'full_name_colored',
        'age_display',
        'nationality_flag',
        'books_count_badge',
        'created_at_formatted'
    ]
    list_filter = ['nationality', 'created_at']
    search_fields = ['first_name', 'last_name', 'biography']
    date_hierarchy = 'birth_date'
    readonly_fields = ['created_at', 'updated_at', 'books_count', 'age_display', 'full_book_list']
    list_per_page = 20
    actions = ['export_authors_with_stats']

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'birth_date', 'age_display', 'nationality'),
            'description': 'Enter the author\'s personal details',
        }),
        ('Biography', {
            'fields': ('biography',),
            'classes': ('wide',),
        }),
        ('Statistics', {
            'fields': ('books_count', 'full_book_list'),
            'classes': ('collapse',),
            'description': 'View author statistics and book list',
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def full_name_colored(self, obj):
        """Display full name with colored badge based on nationality."""
        colors = {
            'American': '#3498db',
            'British': '#e74c3c',
            'Irish': '#2ecc71',
            'Norwegian': '#9b59b6',
            'Colombian': '#f39c12',
        }
        color = colors.get(obj.nationality, '#95a5a6')
        return format_html(
            '<span style="background: linear-gradient(135deg, {} 0%, {} 100%); '
            'color: white; padding: 5px 12px; border-radius: 5px; '
            'font-weight: bold; font-size: 13px; display: inline-block;">'
            '👤 {}</span>',
            color,
            self._darken_color(color),
            obj.full_name
        )

    full_name_colored.short_description = 'Author Name'
    full_name_colored.admin_order_field = 'last_name'

    def age_display(self, obj):
        """Calculate and display author's age or birth year."""
        if not obj.birth_date:
            return format_html(
                '<span style="color: #95a5a6; font-style: italic;">Age unknown</span>'
            )

        today = date.today()
        age = today.year - obj.birth_date.year - (
                (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day)
        )

        # Check if author might be deceased (over 100 years old)
        if age > 100:
            return format_html(
                '<span style="color: #e74c3c; font-weight: bold;">🕊️ {} years '
                '(born {})</span>',
                age,
                obj.birth_date.year
            )

        return format_html(
            '<span style="color: #27ae60; font-weight: bold;">🎂 {} years old</span>',
            age
        )

    age_display.short_description = 'Age'

    def nationality_flag(self, obj):
        """Display nationality with flag emoji."""
        flags = {
            'American': '🇺🇸',
            'British': '🇬🇧',
            'Irish': '🇮🇪',
            'Norwegian': '🇳🇴',
            'Colombian': '🇨🇴',
        }
        flag = flags.get(obj.nationality, '🌍')
        return format_html(
            '<span style="font-size: 16px;">{}</span> <strong>{}</strong>',
            flag,
            obj.nationality or 'Unknown'
        )

    nationality_flag.short_description = 'Nationality'
    nationality_flag.admin_order_field = 'nationality'

    def books_count_badge(self, obj):
        """Display books count with styled badge."""
        count = obj.books_count

        if count == 0:
            color = '#95a5a6'
            icon = '📭'
        elif count <= 2:
            color = '#3498db'
            icon = '📚'
        elif count <= 4:
            color = '#2ecc71'
            icon = '📚📚'
        else:
            color = '#e74c3c'
            icon = '📚📚📚'

        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 4px 10px; border-radius: 12px; font-weight: bold; '
            'font-size: 12px;">{} {} books</span>',
            color,
            icon,
            count
        )

    books_count_badge.short_description = 'Books'

    def created_at_formatted(self, obj):
        """Display creation date in readable format."""
        return format_html(
            '<span style="color: #7f8c8d; font-size: 12px;">📅 {}</span>',
            obj.created_at.strftime('%b %d, %Y')
        )

    created_at_formatted.short_description = 'Added On'
    created_at_formatted.admin_order_field = 'created_at'

    def full_book_list(self, obj):
        """Display full list of books with links."""
        books = obj.books.all()
        if not books:
            return format_html(
                '<p style="color: #95a5a6; font-style: italic;">No books yet</p>'
            )

        book_links = []
        for book in books:
            url = f'/admin/books/book/{book.id}/change/'
            link_html = format_html(
                '<li><a href="{}" style="color: #3498db; text-decoration: none; '
                'font-weight: 500;">{}</a> '
                '<span style="color: #7f8c8d;">({})</span></li>',
                url,
                book.title,
                book.publication_date.year
            )
            book_links.append(link_html)
            final_list_content = ''.join(book_links)

        return mark_safe(
        f'<div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">'
        f'<strong style="color: #2c3e50;">📚 Published Books:</strong>'
        f'<ul style="margin: 10px 0; padding-left: 20px;">{final_list_content}</ul>'
        f'</div>')

    full_book_list.short_description = 'Complete Book List'

    def export_authors_with_stats(self, request, queryset):
        """Custom admin action to export authors with statistics."""
        from django.http import HttpResponse
        import csv

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="authors_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['Full Name', 'Age', 'Nationality', 'Books Count', 'Biography Preview'])

        for author in queryset:
            age = 'Unknown'
            if author.birth_date:
                today = date.today()
                age = today.year - author.birth_date.year

            biography_preview = (author.biography[:50] + '...') if len(author.biography) > 50 else author.biography

            writer.writerow([
                author.full_name,
                age,
                author.nationality,
                author.books_count,
                biography_preview
            ])

        return response

    export_authors_with_stats.short_description = "📊 Export selected authors with statistics"

    @staticmethod
    def _darken_color(hex_color):
        """Helper method to darken a hex color."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.7)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*darkened)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for Book model with custom fields and statistics.
    """
    list_display = [
        'title_with_icon',
        'isbn_formatted',
        'genre_badge',
        'publication_year',
        'price_formatted',
        'pages_with_icon',
        'authors_count_badge',
        'is_recent'
    ]
    list_filter = ['genre', 'publication_date', 'authors']
    search_fields = ['title', 'isbn', 'description']
    date_hierarchy = 'publication_date'
    filter_horizontal = ['authors']
    readonly_fields = [
        'created_at',
        'updated_at',
        'authors_display',
        'book_statistics',
        'price_in_other_currencies'
    ]
    list_per_page = 20
    actions = ['apply_discount']

    fieldsets = (
        ('📖 Book Information', {
            'fields': ('title', 'isbn', 'authors'),
            'description': 'Enter the book\'s basic information',
        }),
        ('📅 Publication Details', {
            'fields': ('publication_date', 'genre', 'pages', 'price'),
            'classes': ('wide',),
        }),
        ('📝 Description', {
            'fields': ('description',),
            'classes': ('collapse',),
        }),
        ('📊 Statistics & Info', {
            'fields': ('authors_display', 'book_statistics', 'price_in_other_currencies'),
            'classes': ('collapse',),
            'description': 'View detailed book information',
        }),
        ('🕐 Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def title_with_icon(self, obj):
        """Display title with genre-specific icon and styling."""
        icons = {
            'fiction': '📚',
            'romance': '💕',
            'biography': '👤',
            'fantasy': '🧙',
            'mystery': '🔍',
            'thriller': '😱',
            'science': '🔬',
            'history': '📜',
            'non_fiction': '📖',
            'other': '📕',
        }
        icon = icons.get(obj.genre, '📕')

        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<span style="font-size: 20px;">{}</span>'
            '<strong style="color: #2c3e50; font-size: 14px;">{}</strong>'
            '</div>',
            icon,
            obj.title
        )

    title_with_icon.short_description = 'Title'
    title_with_icon.admin_order_field = 'title'

    def isbn_formatted(self, obj):
        """Display ISBN with copy button styling."""
        return format_html(
            '<code style="background: #ecf0f1; padding: 4px 8px; '
            'border-radius: 4px; font-family: monospace; color: #2c3e50;">{}</code>',
            obj.isbn
        )

    isbn_formatted.short_description = 'ISBN'
    isbn_formatted.admin_order_field = 'isbn'

    def genre_badge(self, obj):
        """Display genre as colorful badge."""
        colors = {
            'fiction': '#3498db',
            'romance': '#e91e63',
            'biography': '#9c27b0',
            'fantasy': '#673ab7',
            'mystery': '#ff9800',
            'thriller': '#f44336',
            'science': '#00bcd4',
            'history': '#795548',
            'non_fiction': '#607d8b',
            'other': '#9e9e9e',
        }
        color = colors.get(obj.genre, '#9e9e9e')

        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 5px 12px; border-radius: 15px; font-size: 11px; '
            'font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">{}</span>',
            color,
            obj.get_genre_display()
        )

    genre_badge.short_description = 'Genre'
    genre_badge.admin_order_field = 'genre'

    def publication_year(self, obj):
        """Display publication year with decade badge."""
        year = obj.publication_date.year
        decade = (year // 10) * 10

        return format_html(
            '<div style="text-align: center;">'
            '<strong style="color: #2c3e50; font-size: 14px;">{}</strong><br>'
            '<span style="color: #7f8c8d; font-size: 10px;">{}s era</span>'
            '</div>',
            year,
            decade
        )

    publication_year.short_description = 'Published'
    publication_year.admin_order_field = 'publication_date'

    def price_formatted(self, obj):
        """Display price with currency symbol and styling."""
        price = float(obj.price)

        if price < 15:
            color = '#2ecc71'
            label = 'Budget'
        elif price < 20:
            color = '#3498db'
            label = 'Standard'
        else:
            color = '#e74c3c'
            label = 'Premium'

        formatted_price_str = f"{price:.2f}"

        return format_html(
            '<div style="text-align: right;">'
            '<strong style="color: {}; font-size: 16px;">${}</strong><br>'
            '<span style="color: #7f8c8d; font-size: 10px;">{}</span>'
            '</div>',
            color,
            formatted_price_str,
            label
        )

    price_formatted.short_description = 'Price'
    price_formatted.admin_order_field = 'price'

    def pages_with_icon(self, obj):
        """Display pages count with book thickness indicator."""
        if obj.pages < 200:
            icon = '📄'
            thickness = 'Thin'
        elif obj.pages < 400:
            icon = '📖'
            thickness = 'Medium'
        else:
            icon = '📚'
            thickness = 'Thick'

        return format_html(
            '<span title="{} book">{} <strong>{}</strong> pages</span>',
            thickness,
            icon,
            obj.pages
        )

    pages_with_icon.short_description = 'Pages'
    pages_with_icon.admin_order_field = 'pages'

    def authors_count_badge(self, obj):
        """Display number of authors with badge."""
        count = obj.authors.count()

        if count == 0:
            return format_html('<span style="color: #e74c3c;">⚠️ No authors</span>')
        elif count == 1:
            return format_html('<span style="color: #2ecc71;">✅ 1 author</span>')
        else:
            return format_html(
                '<span style="background: #3498db; color: white; '
                'padding: 3px 8px; border-radius: 10px; font-size: 11px;">'
                '👥 {} authors</span>',
                count
            )

    authors_count_badge.short_description = 'Authors'

    def is_recent(self, obj):
        """Indicate if book is recently published (last 5 years)."""
        current_year = date.today().year
        book_year = obj.publication_date.year

        if current_year - book_year <= 5:
            return format_html(
                '<span style="color: #27ae60; font-weight: bold;">🆕 Recent</span>'
            )
        elif current_year - book_year <= 20:
            return format_html(
                '<span style="color: #3498db;">📅 Modern</span>'
            )
        else:
            return format_html(
                '<span style="color: #95a5a6;">📚 Classic</span>'
            )

    is_recent.short_description = 'Status'

    def authors_display(self, obj):
        """Display authors as clickable links with avatars."""
        authors = obj.authors.all()

        if not authors:
            return format_html(
                '<p style="color: #e74c3c;">⚠️ No authors assigned</p>'
            )

        author_cards = []
        for author in authors:
            url = f'/admin/books/author/{author.id}/change/'

            # Get age if available
            age_info = ''
            if author.birth_date:
                today = date.today()
                age = today.year - author.birth_date.year
                age_info = f' ({age} years)'

            card_html = format_html(
                '<div style="background: #f8f9fa; padding: 10px; margin: 5px 0; '
                'border-left: 3px solid #3498db; border-radius: 4px;">'
                '<a href="{}" style="color: #2c3e50; text-decoration: none; '
                'font-weight: 600; font-size: 14px;">👤 {}</a>'
                '<span style="color: #7f8c8d; font-size: 12px;">{}</span><br>'
                '<span style="color: #95a5a6; font-size: 11px;">📍 {}</span>'
                '</div>',
                url,
                author.full_name,
                age_info,
                author.nationality or "Unknown"
            )

            author_cards.append(card_html)
            final_html_content = ''.join(author_cards)

        return mark_safe(
        f'<div style="max-width: 400px;">{final_html_content}</div>'
        )

    authors_display.short_description = 'Authors Detail'

    def book_statistics(self, obj):
        """Display comprehensive book statistics."""

        # Get related statistics
        same_genre_count = Book.objects.filter(genre=obj.genre).count()
        same_year_count = Book.objects.filter(publication_date__year=obj.publication_date.year).count()

        # Calculate price percentile
        cheaper_books = Book.objects.filter(price__lt=obj.price).count()
        total_books = Book.objects.count()
        price_percentile = (cheaper_books / total_books * 100) if total_books > 0 else 0

        percentile_str = f"{price_percentile:.1f}"

        return format_html(
            '<div style="background: #ecf0f1; padding: 15px; border-radius: 8px;">'
            '<h3 style="margin-top: 0; color: #2c3e50;">📊 Book Statistics</h3>'
            '<table style="width: 100%; border-collapse: collapse;">'
            '<tr><td style="padding: 5px;"><strong>Same Genre:</strong></td><td>{} books</td></tr>'
            '<tr><td style="padding: 5px;"><strong>Same Year:</strong></td><td>{} books</td></tr>'
            '<tr><td style="padding: 5px;"><strong>Price Percentile:</strong></td><td>{}%</td></tr>'
            '<tr><td style="padding: 5px;"><strong>Added:</strong></td><td>{}</td></tr>'
            '<tr><td style="padding: 5px;"><strong>Last Updated:</strong></td><td>{}</td></tr>'
            '</table>'
            '</div>',
            same_genre_count,
            same_year_count,
            percentile_str,
            obj.created_at.strftime('%b %d, %Y at %H:%M'),
            obj.updated_at.strftime('%b %d, %Y at %H:%M')
        )

    book_statistics.short_description = 'Statistics'

    def price_in_other_currencies(self, obj):
        """Display price converted to other currencies (example rates)."""
        if obj.price is None:
            return format_html(
                '<p style="color: #e74c3c; font-weight: bold;">⚠️ Cannot convert without price data</p>'
            )
        usd = float(obj.price)
        eur = usd * 0.92  # Example rate
        gbp = usd * 0.79  # Example rate
        pyg = usd * 7300  # Guaraníes paraguayos (tu moneda local!)

        usd_str = f"{usd:.2f}"
        eur_str = f"{eur:.2f}"
        gbp_str = f"{gbp:.2f}"
        pyg_str = f"{pyg:,.0f}"

        return format_html(
            '<div style="background: #fff3cd; padding: 15px; border-radius: 8px; '
            'border: 1px solid #ffc107;">'
            '<h3 style="margin-top: 0; color: #856404;">💱 Currency Conversion</h3>'
            '<table style="width: 100%;">'
            '<tr><td><strong>🇺🇸 USD:</strong></td><td style="text-align: right;">${}</td></tr>'
            '<tr><td><strong>🇪🇺 EUR:</strong></td><td style="text-align: right;">€{}</td></tr>'
            '<tr><td><strong>🇬🇧 GBP:</strong></td><td style="text-align: right;">£{}</td></tr>'
            '<tr><td><strong>🇵🇾 PYG:</strong></td><td style="text-align: right;">₲{}</td></tr>'
            '</table>'
            '<p style="font-size: 10px; color: #856404; margin-bottom: 0;">'
            '* Approximate rates for reference only</p>'
            '</div>',
            usd_str, eur_str, gbp_str, pyg_str
        )

    price_in_other_currencies.short_description = 'Price Conversions'

    @admin.action(description='Apply 10 percent discount to selected books')
    def apply_discount(self, request, queryset):
        """Custom action to apply 10% discount."""
        DISCOUNT_FACTOR = Decimal('0.9')
        updated = 0
        for book in queryset:
            book.price = book.price * DISCOUNT_FACTOR
            book.save()
            updated += 1

        self.message_user(request, f"10% discount applied to {updated} books!")



# Customize admin site headers
admin.site.site_header = "📚 Bookshop Administration"
admin.site.site_title = "Bookshop Admin Portal"
admin.site.index_title = "Welcome to Bookshop Management System"