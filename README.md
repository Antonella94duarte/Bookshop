## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd bookshop
```

### 2. Deploy the application

#### On Linux/Mac:
```bash
chmod +x deploy.sh
./deploy.sh
```

#### On Windows (PowerShell):
```powershell
.\deploy.ps1
```

**Note:** If you get an execution policy error on Windows, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Manual deployment (all platforms):

If you prefer to run commands manually:
```bash
# Build and start containers
docker-compose build
docker-compose up -d

# Wait for database
# (Wait about 10 seconds)

# Run migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Load initial data
docker-compose exec web python manage.py load_initial_data

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### 3. Access the application

- **API Root**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **Authors Endpoint**: http://localhost:8000/api/authors/
- **Books Endpoint**: http://localhost:8000/api/books/

## 📖 API Documentation

### Authors Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/authors/` | List all authors |
| POST | `/api/authors/` | Create a new author |
| GET | `/api/authors/{id}/` | Get author details |
| PUT | `/api/authors/{id}/` | Update author |
| PATCH | `/api/authors/{id}/` | Partial update author |
| DELETE | `/api/authors/{id}/` | Delete author |
| GET | `/api/authors/with_books/` | List authors with book count |
| GET | `/api/authors/top_authors/` | Get top authors by book count |
| GET | `/api/authors/{id}/books/` | Get all books by author |

### Books Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books/` | List all books |
| POST | `/api/books/` | Create a new book |
| GET | `/api/books/{id}/` | Get book details |
| PUT | `/api/books/{id}/` | Update book |
| PATCH | `/api/books/{id}/` | Partial update book |
| DELETE | `/api/books/{id}/` | Delete book |
| GET | `/api/books/by_genre/` | Get books grouped by genre |
| GET | `/api/books/statistics/` | Get book statistics |
| GET | `/api/books/search_books/` | Advanced search |
| POST | `/api/books/{id}/add_author/` | Add author to book |
| POST | `/api/books/{id}/remove_author/` | Remove author from book |

### Query Parameters

**Filtering:**
- `?genre=fiction` - Filter books by genre
- `?nationality=British` - Filter authors by nationality
- `?min_price=10&max_price=20` - Filter books by price range
- `?year=2023` - Filter books by publication year

**Searching:**
- `?search=Harry` - Search in title, description, ISBN

**Ordering:**
- `?ordering=price` - Order by price (ascending)
- `?ordering=-publication_date` - Order by date (descending)

**Pagination:**
- `?page=2` - Get page 2
- `?page_size=20` - Set page size

## 🧪 Running Tests
```bash
docker-compose exec web python manage.py test
```

Run tests with coverage:
```bash
docker-compose exec web python manage.py test --verbosity=2
```

## 🗄️ Database Schema

### Author Model
- `first_name` (CharField)
- `last_name` (CharField)
- `birth_date` (DateField, optional)
- `nationality` (CharField, optional)
- `biography` (TextField, optional)
- `created_at` (DateTimeField, auto)
- `updated_at` (DateTimeField, auto)

### Book Model
- `title` (CharField)
- `isbn` (CharField, unique)
- `publication_date` (DateField)
- `genre` (CharField, choices)
- `pages` (IntegerField)
- `price` (DecimalField)
- `description` (TextField, optional)
- `authors` (ManyToManyField → Author)
- `created_at` (DateTimeField, auto)
- `updated_at` (DateTimeField, auto)

## 🐳 Docker Commands

### Start the application
```bash
docker-compose up -d
```

### Stop the application
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### Access Django shell
```bash
docker-compose exec web python manage.py shell
```

### Create migrations
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Load initial data
```bash
docker-compose exec web python manage.py load_initial_data
```

### Create superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

## 📂 Project Structure
```
Bookshop/
├── books/                      # Main Django app
│   ├── management/
│   │   └── commands/
│   │       └── load_initial_data.py
│   ├── migrations/
│   ├── admin.py               # Admin configuration
│   ├── models.py              # Database models
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views
│   ├── urls.py                # App URLs
│   └── tests.py               # Tests
├── config/                     # Project configuration
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URLs
│   └── wsgi.py
├── docker-compose.yml         # Docker Compose config
├── Dockerfile                 # Docker image config
├── requirements.txt           # Python dependencies
├── deploy.sh                  # Deployment script
├── manage.py                  # Django management
├── .gitignore
└── README.md
```

## 🔍 Example API Usage

### Create an Author
```bash
curl -X POST http://localhost:8000/api/authors/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Ernest",
    "last_name": "Hemingway",
    "birth_date": "1899-07-21",
    "nationality": "American"
  }'
```

### Create a Book
```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Old Man and the Sea",
    "isbn": "9780684801223",
    "publication_date": "1952-09-01",
    "genre": "fiction",
    "pages": 127,
    "price": "12.99",
    "author_ids": [1]
  }'
```

### Get Book Statistics
```bash
curl http://localhost:8000/api/books/statistics/
```

### Search Books
```bash
curl "http://localhost:8000/api/books/search_books/?q=Harry&author=Rowling"
```

## 👤 Author

Liz Antonella Duarte - [GitHub] (https://github.com/Antonella94duarte)

## 🙏 Acknowledgments

- Django Documentation
- Django Rest Framework Documentation
- PostgreSQL Documentation