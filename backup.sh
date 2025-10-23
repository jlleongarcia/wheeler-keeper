#!/bin/bash

# Script para hacer backup de Wheeler Keeper
# Uso: ./backup.sh

set -e

# Configuración
BACKUP_DIR="./backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="wheeler_keeper_backup_$DATE.sql"

# Crear directorio de backups si no existe
# NOTA: Los backups están excluidos de Git en .gitignore
mkdir -p $BACKUP_DIR

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔄 Iniciando backup de Wheeler Keeper...${NC}"

# Verificar que los contenedores estén ejecutándose
if ! docker-compose ps | grep -q "wheeler-keeper-db-1.*Up"; then
    echo -e "${RED}❌ Error: El contenedor de base de datos no está ejecutándose${NC}"
    echo "Ejecuta: docker-compose up -d"
    exit 1
fi

# Hacer backup usando pg_dump
echo -e "${YELLOW}📦 Creando backup...${NC}"
docker-compose exec -T db pg_dump -U wheeler_keeper_user -d wheeler_keeper_db > "$BACKUP_DIR/$BACKUP_FILE"

# Verificar que el backup se creó correctamente
if [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup creado exitosamente:${NC}"
    echo -e "   📁 Archivo: $BACKUP_DIR/$BACKUP_FILE"
    echo -e "   📏 Tamaño: $BACKUP_SIZE"
    
    # Comprimir el backup
    echo -e "${YELLOW}🗜️  Comprimiendo backup...${NC}"
    gzip "$BACKUP_DIR/$BACKUP_FILE"
    COMPRESSED_FILE="$BACKUP_DIR/$BACKUP_FILE.gz"
    COMPRESSED_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup comprimido:${NC}"
    echo -e "   📁 Archivo: $COMPRESSED_FILE"
    echo -e "   📏 Tamaño: $COMPRESSED_SIZE"
else
    echo -e "${RED}❌ Error: No se pudo crear el backup${NC}"
    exit 1
fi

# Limpiar backups antiguos (mantener solo los últimos 10)
echo -e "${YELLOW}🧹 Limpiando backups antiguos...${NC}"
cd $BACKUP_DIR
ls -t wheeler_keeper_backup_*.sql.gz 2>/dev/null | tail -n +11 | xargs -r rm
BACKUP_COUNT=$(ls -1 wheeler_keeper_backup_*.sql.gz 2>/dev/null | wc -l)
echo -e "${GREEN}📊 Backups mantenidos: $BACKUP_COUNT${NC}"

echo -e "${GREEN}🎉 ¡Backup completado exitosamente!${NC}"