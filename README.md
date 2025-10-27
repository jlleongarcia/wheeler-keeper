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

#### 🚀 Quick Start (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/wheeler-keeper.git
   cd wheeler-keeper
   ```

2. **Complete setup with Make**:
   ```bash
   # One-command setup (interactive)
   make first-time-setup
   
   # Or step by step:
   make config-setup    # Copy configuration templates
   # Edit .env and wheeler_keeper/settings.py with your data
   make install         # Build and start
   ```

3. **Access your app**:
   - App: http://localhost:8200
   - Admin: http://localhost:8200/admin
   - **Default login**: Username: `sa`, Password: `superadminpass123`
   - ⚠️ **IMPORTANT**: Change the password on first login for security!

#### ⚙️ Configuration Files

The project uses secure configuration files:
- **`.env`** - Database and email credentials (not tracked by Git)
- **`settings.py`** - Django configuration with your domains (not tracked by Git)
- Templates are provided: `.env.example` and `settings.example.py`

#### 📋 Available Commands

```bash
make help              # See all available commands
make quick-start       # Daily start (when already configured)
make logs             # View real-time logs
make shell            # Access Django shell
make check-config     # Verify configuration
```

#### 🐳 Manual Docker Setup (Alternative)

If you prefer manual Docker commands:

1. **Copy configuration files**:
   ```bash
   cp .env.example .env
   cp wheeler_keeper/settings.example.py wheeler_keeper/settings.py
   ```

2. **Edit configuration files with your specific data**

3. **Build and start**:
   ```bash
   docker-compose up -d --build
   ```

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

## Base de Datos y Backups

### Ubicación de la Base de Datos
La base de datos PostgreSQL se almacena en un volumen de Docker llamado `wheeler-keeper_postgres_data`. 
Los datos están físicamente en: `/var/lib/docker/volumes/wheeler-keeper_postgres_data/_data`

### Hacer Backup
```bash
# Crear backup automático
./backup.sh
```

El script:
- ✅ Crea un backup SQL usando `pg_dump`
- ✅ Comprime el archivo automáticamente
- ✅ Mantiene los últimos 10 backups
- ✅ Guarda los backups en `./backups/`

### Restaurar Backup
```bash
# Restaurar desde un backup específico
./restore.sh backups/wheeler_keeper_backup_YYYYMMDD_HHMMSS.sql.gz
```

⚠️ **ADVERTENCIA**: La restauración elimina todos los datos actuales.

### Backup Manual (Alternativo)
```bash
# Crear backup manual
docker-compose exec db pg_dump -U wheeler_keeper_user wheeler_keeper_db > backup.sql

# Restaurar backup manual
cat backup.sql | docker-compose exec -T db psql -U wheeler_keeper_user -d wheeler_keeper_db
```

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

## 🚀 Installation Guide - Troubleshooting

### ❌ Common Problem: Database Connection Error

If when running `docker-compose up -d` you get this error:

```
django.db.utils.OperationalError: connection to server at "db" failed
```

This happens because Django tries to connect before PostgreSQL is ready.

### ✅ Solution: Use the Makefile

#### Installation with Make (RECOMMENDED)

```bash
# Clone repository
git clone <your-repository>
cd wheeler-keeper

# Automatic installation
make install
```

#### Most useful Make commands

```bash
make help              # See all commands
make install           # First installation
make up                # Start services (first time)  
make quick-start       # Quick start
make down              # Stop everything
make logs              # View logs
make createsuperuser   # Create admin user
make backup-db         # Database backup
```

#### 🔧 Manual Installation (without Make)

If you don't have Make installed:

```bash
# 1. Build images
docker-compose build

# 2. Start ONLY the database
docker-compose up -d db

# 3. WAIT for PostgreSQL to be ready (important!)
sleep 15

# 4. Run migrations
docker-compose run --rm web python manage.py migrate

# 5. Load maintenance types
docker-compose run --rm web python manage.py load_maintenance_types

# 6. Start web application
docker-compose up -d web
```

#### 🏥 If you still have problems

##### Check service status
```bash
docker-compose ps
make status  # with Make
```

##### View detailed logs
```bash
docker-compose logs db      # PostgreSQL logs
docker-compose logs web     # Django logs
make logs                   # with Make
```

##### Complete restart
```bash
docker-compose down -v      # Stop everything
docker-compose up -d db     # Only DB
sleep 15                    # Wait
docker-compose up -d web    # Application
```

##### Clean completely (last resort)
```bash
make clean-all  # Removes EVERYTHING (including data!)
# Or manual:
docker-compose down -v --rmi all
docker system prune -af
```

#### 🎯 Access after installation

- **Web**: http://localhost:8200
- **Admin**: http://localhost:8200/admin
- **Default user**: `sa` / `admin123`

#### 🔍 Why does this problem occur?

1. **Startup order**: Docker Compose starts services in parallel
2. **Dependencies**: Django needs PostgreSQL ready BEFORE starting
3. **Initialization time**: PostgreSQL takes a few seconds to be available
4. **Import queries**: Django forms make queries during import time

#### 🛠 What we have solved?

1. **Makefile**: Controls startup order
2. **Improved entrypoint**: Waits for PostgreSQL before continuing
3. **Lazy forms**: Don't query DB during import
4. **Error handling**: Graceful handling if DB is not available

With these changes the problem should be resolved! 🎉

## Email Notifications Setup

Wheeler Keeper can send email notifications when new users request registration. By default, emails are only shown in console logs.

### For Real Email Delivery

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Configure email settings in `.env`:**
   ```bash
   # Email configuration
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password-here
   ```

3. **For Gmail users - Generate App Password:**

   **Prerequisites:**
   - 2-factor authentication must be enabled
   - Regular account password won't work

   **Steps to get App Password:**
   1. Go to [Google Account Settings](https://myaccount.google.com)
   2. Search for "app passwords" in the page search bar
   3. Or navigate to **Security** → **How you sign in to Google** → **App passwords**
   4. Or try direct URL: https://myaccount.google.com/apppasswords
   5. Generate a new app password for "Wheeler Keeper"
   6. Use the 16-character password in your `.env` file

   **Troubleshooting:**
   - If "App passwords" doesn't appear, ensure 2-factor authentication is enabled
   - The option may be under **Security** → **Google Account Access**

4. **Restart containers:**
   ```bash
   docker-compose restart
   # Or using Make:
   make restart
   ```

### Email Recipients

Notifications are sent to:
1. **Primary:** Admin user (`sa`) email address (if configured in database)
2. **Fallback:** `ADMIN_EMAIL` environment variable (if user `sa` has no email)

### Development Mode (Console Only)

For development without real email delivery:
```bash
# In .env file
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

View emails in container logs:
```bash
docker-compose logs -f web
# Or: make logs
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).