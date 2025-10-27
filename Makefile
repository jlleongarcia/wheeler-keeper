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
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

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

# Comandos de desarrollo
dev-reset: ## Reinicia todo el entorno de desarrollo
	@echo "$(YELLOW)🔄 Reiniciando entorno de desarrollo...$(NC)"
	$(MAKE) down
	$(MAKE) build
	$(MAKE) up

install: ## Primera instalación del proyecto
	@echo "$(GREEN)🎯 Instalación inicial de Wheeler Keeper$(NC)"
	@echo "$(YELLOW)📋 Paso 1: Construyendo imágenes...$(NC)"
	$(MAKE) build
	@echo "$(YELLOW)📋 Paso 2: Configurando aplicación...$(NC)"
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