# Wheeler Keeper - Django Car Maintenance Logger

A Django-based web application for logging and tracking car maintenance records, fully containerized with Docker.

## Features

- **Car Maintenance Logging**: Track all maintenance activities for your vehicle
- **PostgreSQL Database**: Reliable database backend for data persistence
- **Docker Containerization**: Easy deployment and development environment
- **Django Admin Interface**: Built-in admin panel for data management

## Project Structure

```
wheeler-keeper/
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile             # Django app container configuration
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
├── .env                  # Environment variables (not in git)
├── .gitignore           # Git ignore rules
├── wheeler_keeper/      # Django project directory
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py      # Django settings with PostgreSQL config
│   ├── urls.py
│   └── wsgi.py
└── maintenance/         # Django app for car maintenance
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py        # Database models
    ├── tests.py
    ├── views.py
    └── migrations/      # Database migrations
```

## Quick Start

### Prerequisites

- Docker
- Docker Compose

### Installation & Setup

1. **Clone and navigate to the project**:
   ```bash
   cd wheeler-keeper
   ```

2. **Build and start the containers**:
   ```bash
   docker-compose up -d --build
   ```

   The setup automatically:
   - Waits for PostgreSQL to be ready
   - Runs database migrations
   - Creates a default superuser (username: `sa`, password: `superadminpass123`)
   - Collects static files

4. **Access your app**: 
   - App: http://localhost:8200
   - Admin: http://localhost:8200/admin (sa / superadminpass123)
   - Django admin: http://localhost:8200/admin
   - **Default login**: Username: `sa`, Password: `superadminpass123`
   - ⚠️ **IMPORTANT**: Change the password on first login for security!

### Development

#### Local Development (without Docker)

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up local PostgreSQL** or update `.env` for local SQLite:
   ```bash
   # For SQLite (simpler for local dev)
   # Comment out PostgreSQL config in settings.py and use:
   # DATABASES = {
   #     'default': {
   #         'ENGINE': 'django.db.backends.sqlite3',
   #         'NAME': BASE_DIR / 'db.sqlite3',
   #     }
   # }
   ```

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**:
   ```bash
   python manage.py runserver
   ```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database settings (for Docker)
DB_NAME=wheeler_keeper_db
DB_USER=wheeler_keeper_user
DB_PASSWORD=wheeler_keeper_password
DB_HOST=db
DB_PORT=5432
```

## Docker Commands

- **Start containers**: `docker-compose up -d`
- **Stop containers**: `docker-compose down`
- **View logs**: `docker-compose logs web`
- **Execute commands in web container**: `docker-compose exec web <command>`
- **Rebuild containers**: `docker-compose up --build`

## Database

The application uses PostgreSQL in production/Docker environment. The database configuration is handled through environment variables for security and flexibility.

### Database Schema

The `maintenance` app will contain models for:
- Vehicle information
- Maintenance records
- Service categories
- Maintenance schedules

## Next Steps

After setting up the basic structure, you can:

1. **Define Models**: Create vehicle and maintenance record models in `maintenance/models.py`
2. **Create Views**: Implement views for listing, adding, and editing maintenance records
3. **Design Templates**: Create HTML templates for the user interface
4. **Add Forms**: Create Django forms for data input
5. **Implement Search**: Add search and filtering capabilities
6. **Add Authentication**: Implement user authentication for multi-user support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).