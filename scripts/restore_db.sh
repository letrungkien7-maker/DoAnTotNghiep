#!/usr/bin/env bash
# ==============================================================================
# Database Restore Script for PostgreSQL (BDS Smart)
# ==============================================================================
set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <path_to_backup_file.sql.gz | path_to_backup_file.sql>"
    exit 1
fi

BACKUP_FILE="$1"
DB_CONTAINER="${DB_CONTAINER:-bds_postgres}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-real_estate_db}"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file '${BACKUP_FILE}' does not exist!"
    exit 1
fi

echo "=========================================================="
echo "WARNING: Restoring will overwrite existing data in [${DB_NAME}]!"
echo "Restoring from: ${BACKUP_FILE}"
echo "=========================================================="

if [[ "${BACKUP_FILE}" == *.gz ]]; then
    if docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
        echo "Decompressing and piping into container [${DB_CONTAINER}]..."
        gunzip -c "${BACKUP_FILE}" | docker exec -i "${DB_CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}"
    else
        echo "Decompressing and piping into local psql..."
        gunzip -c "${BACKUP_FILE}" | psql -U "${DB_USER}" -d "${DB_NAME}"
    fi
else
    if docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
        docker exec -i "${DB_CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}" < "${BACKUP_FILE}"
    else
        psql -U "${DB_USER}" -d "${DB_NAME}" < "${BACKUP_FILE}"
    fi
fi

echo "Database restoration completed successfully!"
