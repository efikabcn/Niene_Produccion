#!/bin/sh
# ============================================
# Niene Producció - Automatic Backup Script
# Runs daily at 2:00 AM via crond
# Keeps last 30 backups
# ============================================

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILENAME="niene_backup_${TIMESTAMP}.sql.gz"

# Create backup
pg_dump -h db -U niene niene_produccion | gzip > "${BACKUP_DIR}/${FILENAME}"

# Remove backups older than 30 days
find ${BACKUP_DIR} -name "niene_backup_*.sql.gz" -mtime +30 -delete

echo "[$(date)] Backup created: ${FILENAME}"

# Add to crontab on container start
echo "0 2 * * * /backup.sh >> /var/log/backup.log 2>&1" | crontab -
