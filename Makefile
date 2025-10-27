# Wheeler Keeper - Makefile para gestión del proyecto
.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser loaddata clean stop start status

# Variables
COMPOSE_FILE = docker-compose.yml
WEB_SERVICE = web
DB_SERVICE = db

# Colores para output
GREEN = \033[32m
YELLOW = \033[33m
RED = \033[31m
NC = \033[0m # No Color

help: ## Muestra esta ayuda
	@echo "$(GREEN)Wheeler Keeper - Comandos disponibles:$(NC)"
	@echo ""
	@echo "$(YELLOW)🚀 Primera instalación:$(NC)"
	@echo "  $(YELLOW)first-time-setup$(NC)  - Configuración completa para primera vez"
	@echo "  $(YELLOW)config-setup$(NC)      - Solo copiar archivos de configuración"
	@echo "  $(YELLOW)check-config$(NC)      - Verificar configuración"
	@echo "  $(YELLOW)install$(NC)           - Instalar después de configurar"
	@echo ""
	@echo "$(YELLOW)📊 Operaciones diarias:$(NC)"
	@echo "  $(YELLOW)quick-start$(NC)       - Inicio rápido"
	@echo "  $(YELLOW)up$(NC)                - Levantar servicios completo"
	@echo "  $(YELLOW)down$(NC)              - Detener servicios"
	@echo "  $(YELLOW)restart$(NC)           - Reiniciar servicios"
	@echo ""
	@echo "$(YELLOW)🛠️  Desarrollo:$(NC)"
	@echo "  $(YELLOW)logs$(NC)              - Ver logs en tiempo real"
	@echo "  $(YELLOW)shell$(NC)             - Acceder al shell de Django"
	@echo "  $(YELLOW)migrate$(NC)           - Ejecutar migraciones"
	@echo "  $(YELLOW)createsuperuser$(NC)   - Crear usuario administrador"
	@echo ""
	@echo "$(YELLOW)🔧 Utilidades:$(NC)"
	@echo "  $(YELLOW)health$(NC)            - Verificar estado de servicios"
	@echo "  $(YELLOW)backup-db$(NC)         - Hacer backup de la base de datos"
	@echo "  $(YELLOW)clean-all$(NC)         - Limpiar todo (⚠️ PELIGROSO)"
	@echo ""
	@echo "$(GREEN)Para ver todos los comandos: grep '^[a-zA-Z_-]*:.*##' Makefile$(NC)"

build: ## Construye las imágenes Docker
	@echo "$(GREEN)🔨 Construyendo imágenes Docker...$(NC)"
	docker-compose build --no-cache

up: ## Levanta los servicios (primera vez o completo)
	@echo "$(GREEN)🚀 Iniciando Wheeler Keeper...$(NC)"
	@echo "$(YELLOW)⏳ Paso 1: Levantando base de datos...$(NC)"
	docker-compose up -d $(DB_SERVICE)
	@echo "$(YELLOW)⏳ Esperando que PostgreSQL esté listo...$(NC)"
	@sleep 10
	@echo "$(YELLOW)⏳ Paso 2: Ejecutando migraciones...$(NC)"
	docker-compose run --rm $(WEB_SERVICE) python manage.py migrate
	@echo "$(YELLOW)⏳ Paso 3: Cargando tipos de mantenimiento...$(NC)"
	docker-compose run --rm $(WEB_SERVICE) python manage.py load_maintenance_types || true
	@echo "$(YELLOW)⏳ Paso 4: Levantando aplicación web...$(NC)"
	docker-compose up -d $(WEB_SERVICE)
	@echo "$(GREEN)✅ Wheeler Keeper está listo!$(NC)"
	@echo "$(YELLOW)🌐 Accede en: http://localhost:8200$(NC)"

quick-start: ## Inicio rápido (cuando ya está configurado)
	@echo "$(GREEN)⚡ Inicio rápido de Wheeler Keeper...$(NC)"
	docker-compose up -d

down: ## Detiene y elimina los contenedores
	@echo "$(YELLOW)🛑 Deteniendo Wheeler Keeper...$(NC)"
	docker-compose down

restart: ## Reinicia los servicios
	@echo "$(YELLOW)🔄 Reiniciando Wheeler Keeper...$(NC)"
	docker-compose restart

stop: ## Detiene los servicios sin eliminar contenedores
	@echo "$(YELLOW)⏸️  Deteniendo servicios...$(NC)"
	docker-compose stop

start: ## Inicia servicios previamente detenidos
	@echo "$(GREEN)▶️  Iniciando servicios...$(NC)"
	docker-compose start

logs: ## Muestra los logs de todos los servicios
	docker-compose logs -f

logs-web: ## Muestra los logs solo del servicio web
	docker-compose logs -f $(WEB_SERVICE)

logs-db: ## Muestra los logs solo de la base de datos
	docker-compose logs -f $(DB_SERVICE)

shell: ## Abre shell de Django en el contenedor web
	docker-compose exec $(WEB_SERVICE) python manage.py shell

bash: ## Abre bash en el contenedor web
	docker-compose exec $(WEB_SERVICE) bash

migrate: ## Ejecuta las migraciones pendientes
	@echo "$(GREEN)📊 Ejecutando migraciones...$(NC)"
	docker-compose exec $(WEB_SERVICE) python manage.py migrate

makemigrations: ## Genera nuevas migraciones
	@echo "$(GREEN)📝 Generando migraciones...$(NC)"
	docker-compose exec $(WEB_SERVICE) python manage.py makemigrations
	@echo "$(YELLOW)⚠️  Recuerda cambiar permisos si es necesario:$(NC)"
	@echo "   sudo chown -R $$USER:$$USER ./maintenance/migrations/"

createsuperuser: ## Crea un superusuario
	@echo "$(GREEN)👤 Creando superusuario...$(NC)"
	docker-compose exec $(WEB_SERVICE) python manage.py createsuperuser

loaddata: ## Carga los tipos de mantenimiento
	@echo "$(GREEN)📦 Cargando tipos de mantenimiento...$(NC)"
	docker-compose exec $(WEB_SERVICE) python manage.py load_maintenance_types

backup-db: ## Hace backup de la base de datos
	@echo "$(GREEN)💾 Creando backup de la base de datos...$(NC)"
	docker-compose exec $(DB_SERVICE) pg_dump -U wheeler_keeper_user wheeler_keeper_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

status: ## Muestra el estado de los contenedores
	@echo "$(GREEN)📊 Estado de los servicios:$(NC)"
	docker-compose ps

clean: ## Limpia contenedores, volúmenes e imágenes no utilizados
	@echo "$(RED)🧹 Limpiando recursos Docker...$(NC)"
	@echo "$(YELLOW)⚠️  Esto eliminará contenedores, volúmenes e imágenes no utilizados$(NC)"
	@read -p "¿Estás seguro? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

clean-all: ## Limpia TODO (incluyendo volúmenes de datos)
	@echo "$(RED)🚨 LIMPIEZA COMPLETA - SE PERDERÁN TODOS LOS DATOS$(NC)"
	@read -p "¿Estás ABSOLUTAMENTE seguro? Escribe 'DELETE' para confirmar: " confirm && [ "$$confirm" = "DELETE" ]
	docker-compose down -v --rmi all
	docker system prune -af
	docker volume prune -af

fix-permissions: ## Arregla permisos de archivos generados por Docker
	@echo "$(GREEN)🔧 Arreglando permisos...$(NC)"
	sudo chown -R $$USER:$$USER ./maintenance/migrations/
	sudo chown -R $$USER:$$USER ./staticfiles/ || true

setup: build up ## Configuración inicial completa (build + up)

health: ## Verifica el estado de salud de los servicios
	@echo "$(GREEN)🏥 Verificando salud de los servicios...$(NC)"
	@echo "Base de datos:"
	@docker-compose exec $(DB_SERVICE) pg_isready -U wheeler_keeper_user || echo "$(RED)❌ DB no disponible$(NC)"
	@echo "Aplicación web:"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8200/ || echo "$(RED)❌ Web no disponible$(NC)"

check-config: ## Verifica la configuración antes de instalar
	@echo "$(GREEN)🔍 Verificando configuración...$(NC)"
	@echo ""
	@echo "$(YELLOW)📁 Archivos de configuración:$(NC)"
	@if [ -f .env ]; then \
		echo "   ✅ .env existe"; \
	else \
		echo "   ❌ .env falta - ejecuta: make config-setup"; \
	fi
	@if [ -f wheeler_keeper/settings.py ]; then \
		echo "   ✅ settings.py existe"; \
	else \
		echo "   ❌ settings.py falta - ejecuta: make config-setup"; \
	fi
	@echo ""
	@echo "$(YELLOW)🔐 Verificación de seguridad:$(NC)"
	@if git check-ignore .env >/dev/null 2>&1; then \
		echo "   ✅ .env está en .gitignore"; \
	else \
		echo "   ⚠️  .env NO está en .gitignore"; \
	fi
	@if git check-ignore wheeler_keeper/settings.py >/dev/null 2>&1; then \
		echo "   ✅ settings.py está en .gitignore"; \
	else \
		echo "   ⚠️  settings.py NO está en .gitignore"; \
	fi

# Comandos de desarrollo
dev-reset: ## Reinicia todo el entorno de desarrollo
	@echo "$(YELLOW)🔄 Reiniciando entorno de desarrollo...$(NC)"
	$(MAKE) down
	$(MAKE) build
	$(MAKE) up

config-setup: ## Copia archivos de configuración desde templates
	@echo "$(GREEN)⚙️  Configurando archivos iniciales...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)📄 Copiando .env.example → .env$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✅ Archivo .env creado$(NC)"; \
		echo "$(YELLOW)⚠️  EDITA .env con tu configuración específica$(NC)"; \
	else \
		echo "$(YELLOW)ℹ️  .env ya existe, omitiendo...$(NC)"; \
	fi
	@if [ ! -f wheeler_keeper/settings.py ]; then \
		echo "$(YELLOW)📄 Copiando settings.example.py → settings.py$(NC)"; \
		cp wheeler_keeper/settings.example.py wheeler_keeper/settings.py; \
		echo "$(GREEN)✅ Archivo settings.py creado$(NC)"; \
		echo "$(YELLOW)⚠️  EDITA settings.py con tus dominios reales$(NC)"; \
	else \
		echo "$(YELLOW)ℹ️  settings.py ya existe, omitiendo...$(NC)"; \
	fi
	@echo "$(GREEN)🎯 Configuración completada!$(NC)"
	@echo ""
	@echo "$(YELLOW)📝 SIGUIENTE PASO:$(NC)"
	@echo "   1. Edita .env con tu configuración de base de datos y email"
	@echo "   2. Edita wheeler_keeper/settings.py con tus dominios"
	@echo "   3. Ejecuta: make install"

install: ## Primera instalación del proyecto
	@echo "$(GREEN)🎯 Instalación inicial de Wheeler Keeper$(NC)"
	@echo "$(YELLOW)📋 Paso 1: Verificando configuración...$(NC)"
	@if [ ! -f .env ] || [ ! -f wheeler_keeper/settings.py ]; then \
		echo "$(RED)❌ Faltan archivos de configuración$(NC)"; \
		echo "$(YELLOW)Ejecuta primero: make config-setup$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)📋 Paso 2: Construyendo imágenes...$(NC)"
	$(MAKE) build
	@echo "$(YELLOW)📋 Paso 3: Configurando aplicación...$(NC)"
	$(MAKE) up
	@echo "$(GREEN)✅ ¡Instalación completada!$(NC)"
	@echo ""
	@echo "$(GREEN)🎉 Wheeler Keeper está listo para usar:$(NC)"
	@echo "   🌐 Web: http://localhost:8200"
	@echo "   ⚙️  Admin: http://localhost:8200/admin"
	@echo ""
	@echo "$(YELLOW)🔧 Comandos útiles:$(NC)"
	@echo "   make quick-start  - Inicio rápido"
	@echo "   make createsuperuser - Crear usuario administrador"
	@echo "   make logs        - Ver logs"
	@echo "   make help        - Ver todos los comandos"

first-time-setup: ## Configuración completa para primera vez (config + install)
	@echo "$(GREEN)🚀 Configuración inicial completa$(NC)"
	$(MAKE) config-setup
	@echo ""
	@echo "$(YELLOW)⏸️  PAUSA: Configura tus archivos ahora$(NC)"
	@echo "   📝 Edita .env con tus credenciales"
	@echo "   📝 Edita wheeler_keeper/settings.py con tus dominios"
	@read -p "Presiona ENTER cuando hayas terminado la configuración..." dummy
	$(MAKE) install