#!/usr/bin/env bash
# ==============================================================================
# Database Backup Script for PostgreSQL (BDS Smart)
# ==============================================================================
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/bds_backup_${TIMESTAMP}.sql.gz"
RETENTION_DAYS="${RETENTION_DAYS:-14}"

# Database variables
DB_CONTAINER="${DB_CONTAINER:-bds_postgres}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-real_estate_db}"

mkdir -p "${BACKUP_DIR}"

echo "=========================================================="
echo "Starting PostgreSQL backup: ${DB_NAME} at $(date)"
echo "Target backup file: ${BACKUP_FILE}"
echo "=========================================================="

if docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
    echo "Dumping database directly from running container [${DB_CONTAINER}]..."
    docker exec -t "${DB_CONTAINER}" pg_dump -U "${DB_USER}" -d "${DB_NAME}" --clean --if-exists | gzip > "${BACKUP_FILE}"
else
    echo "Docker container not detected; attempting direct pg_dump..."
    pg_dump -U "${DB_USER}" -d "${DB_NAME}" --clean --if-exists | gzip > "${BACKUP_FILE}"
fi

BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
echo "Backup completed successfully! Size: ${BACKUP_SIZE}"

# Clean up older backups beyond retention days
echo "Purging backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -type f -name "bds_backup_*.sql.gz" -mtime +"${RETENTION_DAYS}" -exec rm -f {} +
echo "Backup cycle finished clean."
