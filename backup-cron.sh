#!/bin/bash

# Wheeler Keeper - cron-safe weekly backup script
# Uses docker exec directly (no dependency on docker-compose or working directory)

set -e

PROJECT_DIR="/home/jlleongarcia/Documents/Github_projects/wheeler-keeper"
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="wheeler_keeper_backup_$DATE.sql"
LOG_FILE="$BACKUP_DIR/backup.log"

DOCKER="/usr/bin/docker"
DB_CONTAINER="wheeler-keeper-db-1"

mkdir -p "$BACKUP_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting Wheeler Keeper backup..."

if ! $DOCKER inspect "$DB_CONTAINER" --format '{{.State.Running}}' 2>/dev/null | grep -q "true"; then
    log "ERROR: Container $DB_CONTAINER is not running. Aborting."
    exit 1
fi

$DOCKER exec "$DB_CONTAINER" pg_dump -U wheeler_keeper_user -d wheeler_keeper_db > "$BACKUP_DIR/$BACKUP_FILE"

if [ ! -f "$BACKUP_DIR/$BACKUP_FILE" ] || [ ! -s "$BACKUP_DIR/$BACKUP_FILE" ]; then
    log "ERROR: Backup file was not created or is empty."
    exit 1
fi

gzip "$BACKUP_DIR/$BACKUP_FILE"
COMPRESSED_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE.gz" | cut -f1)
log "Backup created: $BACKUP_DIR/$BACKUP_FILE.gz ($COMPRESSED_SIZE)"

# Keep only the last 10 backups
cd "$BACKUP_DIR"
ls -t wheeler_keeper_backup_*.sql.gz 2>/dev/null | tail -n +11 | xargs -r rm
BACKUP_COUNT=$(ls -1 wheeler_keeper_backup_*.sql.gz 2>/dev/null | wc -l)
log "Backup completed. Total backups kept: $BACKUP_COUNT"
