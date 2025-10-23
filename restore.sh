#!/bin/bash

# Script para restaurar backup de Wheeler Keeper
# Uso: ./restore.sh <archivo_backup.sql.gz>

set -e

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar argumentos
if [ $# -eq 0 ]; then
    echo -e "${RED}❌ Error: Debes especificar el archivo de backup${NC}"
    echo "Uso: ./restore.sh <archivo_backup.sql.gz>"
    echo ""
    echo "Backups disponibles:"
    ls -la backups/wheeler_keeper_backup_*.sql.gz 2>/dev/null || echo "No hay backups disponibles"
    exit 1
fi

BACKUP_FILE="$1"

# Verificar que el archivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Error: El archivo $BACKUP_FILE no existe${NC}"
    exit 1
fi

echo -e "${YELLOW}🔄 Iniciando restauración desde: $BACKUP_FILE${NC}"

# Verificar que los contenedores estén ejecutándose
if ! docker-compose ps | grep -q "wheeler-keeper-db-1.*Up"; then
    echo -e "${RED}❌ Error: El contenedor de base de datos no está ejecutándose${NC}"
    echo "Ejecuta: docker-compose up -d"
    exit 1
fi

# Confirmar la restauración (¡PELIGROSO!)
echo -e "${RED}⚠️  ADVERTENCIA: Esta operación eliminará todos los datos actuales${NC}"
read -p "¿Estás seguro de que deseas continuar? (escribe 'SI' para confirmar): " confirm

if [ "$confirm" != "SI" ]; then
    echo -e "${YELLOW}❌ Restauración cancelada${NC}"
    exit 0
fi

# Parar la aplicación web temporalmente
echo -e "${YELLOW}⏸️  Parando aplicación web...${NC}"
docker-compose stop web

# Descomprimir y restaurar
echo -e "${YELLOW}📦 Restaurando backup...${NC}"

if [[ "$BACKUP_FILE" == *.gz ]]; then
    # Archivo comprimido
    gunzip -c "$BACKUP_FILE" | docker-compose exec -T db psql -U wheeler_keeper_user -d wheeler_keeper_db
else
    # Archivo sin comprimir
    cat "$BACKUP_FILE" | docker-compose exec -T db psql -U wheeler_keeper_user -d wheeler_keeper_db
fi

# Reiniciar la aplicación web
echo -e "${YELLOW}▶️  Reiniciando aplicación web...${NC}"
docker-compose start web

echo -e "${GREEN}✅ ¡Restauración completada exitosamente!${NC}"
echo -e "${GREEN}🌐 La aplicación está disponible en: http://localhost:8200${NC}"