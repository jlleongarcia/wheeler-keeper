#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Wheeler Keeper - Iniciando entrypoint...${NC}"

# Wait for database to be ready
echo -e "${YELLOW}⏳ Esperando a que PostgreSQL esté disponible...${NC}"
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "\q" > /dev/null 2>&1; do
  echo -e "${YELLOW}   PostgreSQL no está listo - esperando 2 segundos...${NC}"
  sleep 2
done

echo -e "${GREEN}✅ PostgreSQL está disponible!${NC}"

# Additional wait to ensure DB is fully ready
echo -e "${YELLOW}⏳ Esperando 5 segundos adicionales para asegurar que DB está completamente listo...${NC}"
sleep 5

# Run migrations
echo -e "${GREEN}📊 Ejecutando migraciones...${NC}"
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput

# Load maintenance types
echo -e "${GREEN}📦 Cargando tipos de mantenimiento...${NC}"
python manage.py load_maintenance_types || true

# Create default superuser
echo -e "${GREEN}👤 Creando superusuario por defecto...${NC}"
python manage.py create_default_superuser || true

# Collect static files
echo -e "${GREEN}📁 Recolectando archivos estáticos...${NC}"
python manage.py collectstatic --noinput || true

echo -e "${GREEN}🎉 Entrypoint completado exitosamente!${NC}"

# Execute the main command
exec "$@"