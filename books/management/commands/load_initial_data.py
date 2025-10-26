from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date
from decimal import Decimal

from books.models import Author, Book


class Command(BaseCommand):
    help = 'Load initial data for books and authors'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading initial data...')

        with transaction.atomic():
            # Clear existing data
            Book.objects.all().delete()
            Author.objects.all().delete()

            # Create authors
            authors_data = [
                {
                    'first_name': 'Elizabeth',
                    'last_name': 'Gilbert',
                    'birth_date': date(1969, 7, 18),
                    'nationality': 'American',
                    'biography': 'American journalist and author best known for her memoir Eat, Pray, Love.'
                },
                {
                    'first_name': 'Jostein',
                    'last_name': 'Gaarder',
                    'birth_date': date(1952, 8, 8),
                    'nationality': 'Norwegian',
                    'biography': 'Norwegian intellectual and author of several novels, short stories, and children\'s books.'
                },
                {
                    'first_name': 'Cecelia',
                    'last_name': 'Ahern',
                    'birth_date': date(1981, 9, 30),
                    'nationality': 'Irish',
                    'biography': 'Irish novelist known for her romantic and emotional stories.'
                },
                {
                    'first_name': 'Oliver',
                    'last_name': 'Bowden',
                    'birth_date': None,  # Pseudonym, exact birth date not public
                    'nationality': 'British',
                    'biography': 'Pseudonym of an author who writes novels based on the Assassin\'s Creed video game series.'
                },
            ]

            authors = {}
            for author_data in authors_data:
                author = Author.objects.create(**author_data)
                authors[f"{author.first_name} {author.last_name}"] = author
                self.stdout.write(f'Created author: {author.full_name}')

            # Create books
            books_data = [
                # Elizabeth Gilbert's books
                {
                    'title': 'The Signature of All Things',
                    'isbn': '9780670024856',
                    'publication_date': date(2013, 10, 1),
                    'genre': 'fiction',
                    'pages': 512,
                    'price': Decimal('16.99'),
                    'description': 'A novel spanning much of the eighteenth and nineteenth centuries, following the life of botanist Alma Whittaker.',
                    'authors': ['Elizabeth Gilbert']
                },
                {
                    'title': 'Eat, Pray, Love',
                    'isbn': '9780143038412',
                    'publication_date': date(2006, 2, 16),
                    'genre': 'biography',
                    'pages': 352,
                    'price': Decimal('15.99'),
                    'description': 'A memoir of one woman\'s journey through Italy, India, and Indonesia in search of self-discovery.',
                    'authors': ['Elizabeth Gilbert']
                },
                # Jostein Gaarder's books
                {
                    'title': "Sophie's World: A Novel About the History of Philosophy",
                    'isbn': '9780374530716',
                    'publication_date': date(1991, 1, 1),
                    'genre': 'fiction',
                    'pages': 518,
                    'price': Decimal('17.99'),
                    'description': 'A novel that serves as a basic and comprehensible introduction to Western philosophy.',
                    'authors': ['Jostein Gaarder']
                },
                {
                    'title': 'The Orange Girl',
                    'isbn': '9780374356934',
                    'publication_date': date(2003, 9, 1),
                    'genre': 'fiction',
                    'pages': 192,
                    'price': Decimal('13.99'),
                    'description': 'A story about a boy who receives a letter from his father who died when he was four years old.',
                    'authors': ['Jostein Gaarder']
                },
                # Cecelia Ahern's books
                {
                    'title': 'Where Rainbows End',
                    'isbn': '9788466320450',
                    'publication_date': date(2004, 2, 5),
                    'genre': 'romance',
                    'pages': 352,
                    'price': Decimal('14.99'),
                    'description': 'A novel about lifelong friends Alex and Rosie, told through letters, emails, and instant messages.',
                    'authors': ['Cecelia Ahern']
                },
                {
                    'title': 'P.S. I Love You',
                    'isbn': '9780786890750',
                    'publication_date': date(2004, 1, 1),
                    'genre': 'romance',
                    'pages': 448,
                    'price': Decimal('14.99'),
                    'description': 'A heartwarming story about a young widow who receives letters from her late husband.',
                    'authors': ['Cecelia Ahern']
                },
                # Oliver Bowden's Assassin's Creed books
                {
                    'title': "Assassin's Creed: Renaissance",
                    'isbn': '9780441018932',
                    'publication_date': date(2009, 11, 24),
                    'genre': 'fiction',
                    'pages': 512,
                    'price': Decimal('18.99'),
                    'description': 'The first novel based on the Assassin\'s Creed video game series, following Ezio Auditore in Renaissance Italy.',
                    'authors': ['Oliver Bowden']
                },
                {
                    'title': "Assassin's Creed: Brotherhood",
                    'isbn': '9780441020386',
                    'publication_date': date(2010, 11, 23),
                    'genre': 'fiction',
                    'pages': 512,
                    'price': Decimal('18.99'),
                    'description': 'The second book in the series, continuing Ezio\'s journey as he builds the Brotherhood of Assassins.',
                    'authors': ['Oliver Bowden']
                },
                {
                    'title': "Assassin's Creed: The Secret Crusade",
                    'isbn': '9780441020676',
                    'publication_date': date(2011, 6, 28),
                    'genre': 'fiction',
                    'pages': 496,
                    'price': Decimal('18.99'),
                    'description': 'The third book, telling the story of Altaïr Ibn-La\'Ahad during the Third Crusade.',
                    'authors': ['Oliver Bowden']
                },
            ]

            for book_data in books_data:
                author_names = book_data.pop('authors')
                book = Book.objects.create(**book_data)

                for author_name in author_names:
                    book.authors.add(authors[author_name])

                self.stdout.write(f'Created book: {book.title}')

            self.stdout.write(self.style.SUCCESS(
                f'\nSuccessfully loaded {Author.objects.count()} authors '
                f'and {Book.objects.count()} books'
            ))