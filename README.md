# Wheeler Keeper - Django Car Maintenance Logger

A **complete and production-ready** Django-based web application for comprehensive car maintenance logging and tracking, featuring automated email notifications, multi-item cost management, and user-friendly interfaces. Fully containerized with Docker for easy deployment.

## Features

- **Car Maintenance Logging**: Track all maintenance activities for your vehicle
- **Automated Email Notifications**: Smart system that automatically notifies users about upcoming or overdue maintenance (no external cron jobs required)
- **Multi-Item Cost Tracking**: Separate labor costs from parts with taxes calculation support
- **User-Friendly Interface**: Clean, intuitive interface without admin panel complexity
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

The `maintenance` app contains complete models for:
- **Vehiculo**: Vehicle information (make, model, year, current mileage)
- **TipoMantenimiento**: Maintenance service categories with default intervals
- **RegistroMantenimiento**: Main maintenance record entries
- **ItemMantenimiento**: Individual maintenance items with cost breakdown (labor vs parts)
- **IntervaloMantenimiento**: Custom maintenance intervals per vehicle
- **UserRegistrationRequest**: User registration system with email approval
- **NotificacionMantenimiento**: Automated notification tracking and anti-spam

## Current Implementation Status

Wheeler Keeper is a **fully functional** car maintenance logging application with advanced features:

### ✅ **Completed Features**
1. **Models & Database**: ✅ Complete vehicle and maintenance record models with multi-item support
2. **User Interface**: ✅ Clean, user-friendly interface without admin complexity 
3. **Forms & Validation**: ✅ Advanced Django forms with JavaScript-enhanced multi-item entry
4. **Authentication**: ✅ Multi-user support with registration system and email notifications
5. **Cost Tracking**: ✅ Separate labor costs from parts with IVA (tax) calculation
6. **Automated Notifications**: ✅ Smart email notification system for upcoming/overdue maintenance
7. **Admin Panel**: ✅ Complete admin interface for management and monitoring

### 🚀 **Ready to Use**
The application is production-ready with:
- Multi-item maintenance logging
- Cost separation (labor vs parts)
- Tax calculation (IVA support)
- Automated email reminders
- User registration system
- Complete admin oversight

### 🔮 **Future Enhancements** 
Possible future improvements:
1. **Mobile App**: Native mobile application
2. **Advanced Analytics**: Maintenance cost trends and analytics
3. **Integration APIs**: Connect with third-party services
4. **Inventory Management**: Parts inventory tracking
5. **Service Provider Network**: Connect with local mechanics
6. **Vehicle History Reports**: Generate comprehensive maintenance reports

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

## Automated Maintenance Notifications

Wheeler Keeper includes a comprehensive **automated email notification system** that alerts users about upcoming or overdue maintenance **without requiring external cron job configuration**.

### Key Features

#### ✅ **Smart Detection**
- Overdue maintenance by time or mileage
- Upcoming maintenance (≤30 days or ≤1000 km)
- Automatic calculation based on custom or default intervals

#### ✅ **Anti-Spam System**
- Only one notification per maintenance type every 24 hours
- Complete tracking of sent notifications in database
- Automatic prevention of duplicate notifications

#### ✅ **Transparent Integration**
- **No external configuration required** (no cron jobs)
- Executes automatically during normal navigation
- Users don't need to log in daily

#### ✅ **Professional Emails**
- Responsive HTML templates with professional design
- Urgency classification (🚨 overdue vs 🔧 upcoming)
- Vehicle grouping for clarity
- Detailed information for each maintenance item

### How It Works

#### 1. **Smart Middleware**
The system uses Django middleware (`NotificacionesProgramadasMiddleware`) that:
- Activates when users navigate through the application
- Checks once per day per user for pending maintenance
- Uses internal cache to avoid excessive checks
- Runs silently without affecting user experience

#### 2. **Management Command**
```bash
# Manual verification (test mode)
docker-compose exec web python manage.py enviar_notificaciones_mantenimiento --test-mode

# Specific user verification
docker-compose exec web python manage.py enviar_notificaciones_mantenimiento --user-email user@example.com

# Silent mode (used by middleware)
docker-compose exec web python manage.py enviar_notificaciones_mantenimiento --silencioso --usuario-id 123
```

#### 3. **Tracking Model**
- `NotificacionMantenimiento`: Records each sent notification
- Prevents spam with 24-hour checks
- Stores metadata: alert type, mileage, sending success

### Configuration

#### 1. **Middleware (Already Active)**
In `settings.py`:
```python
MIDDLEWARE = [
    # ... other middlewares
    'maintenance.middleware.NotificacionesProgramadasMiddleware',
]
```

#### 2. **Email Configuration**
Make sure your `settings.py` or `.env` includes:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-user@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'Wheeler Keeper <no-reply@your-domain.com>'
```

### Notification Types

#### 🚨 **Overdue**
- **By time**: Maintenance that should have been done X days ago
- **By mileage**: Vehicle exceeded recommended mileage

#### 🔧 **Upcoming**
- **By time**: Maintenance due in ≤30 days
- **By mileage**: Maintenance due in ≤1000 km

### Integrated System Advantages

#### ✅ **No External Dependencies**
- No need to configure cron jobs
- No root server access required
- Works on any Django-supporting hosting

#### ✅ **Delivery Guarantee**
- Executes automatically with normal user activity
- If one user doesn't log in, it runs when another user navigates
- Periodic verification ensured while application is active

#### ✅ **Simplified Maintenance**
- All code integrated into Django application
- Logs accessible from the application
- Complete administration from Django panel

### Admin Panel

You can view complete notification history at:
**Django Admin > MAINTENANCE > Notificaciones de Mantenimiento**

#### Available Information:
- Notified user
- Vehicle and maintenance type
- Alert type (overdue/upcoming, time/mileage)
- Send date and time
- Email status (sent/failed)
- Vehicle mileage at notification time

### Manual Command

For administrators who want to force checks:

```bash
# Check all users (test mode)
docker-compose exec web python manage.py enviar_notificaciones_mantenimiento --test-mode

# Send real notifications
docker-compose exec web python manage.py enviar_notificaciones_mantenimiento

# Specific user
docker-compose exec web python manage.py enviar_notificaciones_mantenimiento --user-email john@example.com
```

### Logs and Debugging

System logs are stored in Django logger:
```python
import logging
logger = logging.getLogger(__name__)
```

For debugging, run in test mode:
```bash
docker-compose exec web python manage.py enviar_notificaciones_mantenimiento --test-mode
```

### Important Notes

1. **First Execution**: System starts working immediately after deployment
2. **Frequency**: Maximum one check per user per day
3. **Anti-Spam**: One notification per maintenance type every 24 hours
4. **Performance**: Minimal navigation impact (asynchronous execution)
5. **Scalability**: Works efficiently with multiple users

The system is designed to be **completely automatic and transparent**, providing an excellent user experience without additional configuration.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).