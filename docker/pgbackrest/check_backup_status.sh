#!/bin/bash
# =============================================================================
# Daily backup verification script for CRM Protegrt
# Cron: 0 8 * * * /opt/protegrt/scripts/check_backup_status.sh
#
# Checks:
#   1. Last backup was successful
#   2. Last backup is not older than 26 hours
#   3. Integrity verification passes
#
# Alerts via Telegram if any check fails.
# Required env vars: TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID
# =============================================================================

set -euo pipefail

# Load environment variables
if [ -f /opt/protegrt/.env ]; then
    source /opt/protegrt/.env
fi

STANZA="protegrt"
MAX_AGE_HOURS=26
LOG_FILE="/var/log/pgbackrest/verify.log"

send_alert() {
    local message="$1"
    if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_ADMIN_CHAT_ID:-}" ]; then
        curl -sf "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_ADMIN_CHAT_ID}" \
            -d "text=🔴 ALERTA BACKUP CRM Protegrt: ${message}" \
            -d "parse_mode=HTML" > /dev/null 2>&1 || true
    fi
    echo "$(date '+%Y-%m-%d %H:%M:%S') ALERT: ${message}" >> "$LOG_FILE"
}

log_ok() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') OK: $1" >> "$LOG_FILE"
}

# 1. Get last backup info
BACKUP_INFO=$(pgbackrest --stanza="$STANZA" info --output=json 2>/dev/null) || {
    send_alert "No se pudo obtener informacion del backup. pgBackRest puede estar mal configurado."
    exit 1
}

# Parse last backup
LAST_BACKUP=$(echo "$BACKUP_INFO" | jq -r '.[0].backup[-1]' 2>/dev/null)
if [ "$LAST_BACKUP" = "null" ] || [ -z "$LAST_BACKUP" ]; then
    send_alert "No se encontro ningun backup. Verificar configuracion pgBackRest."
    exit 1
fi

# 2. Check backup status
BACKUP_TYPE=$(echo "$LAST_BACKUP" | jq -r '.type')
BACKUP_ERROR=$(echo "$LAST_BACKUP" | jq -r '.error // false')
BACKUP_TIMESTAMP=$(echo "$LAST_BACKUP" | jq -r '.timestamp.stop')

if [ "$BACKUP_ERROR" = "true" ]; then
    send_alert "Ultimo backup (${BACKUP_TYPE}) termino con error."
    exit 1
fi

# 3. Check backup age
BACKUP_EPOCH=$(date -d "$BACKUP_TIMESTAMP" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%S" "$BACKUP_TIMESTAMP" +%s 2>/dev/null)
NOW_EPOCH=$(date +%s)
AGE_HOURS=$(( (NOW_EPOCH - BACKUP_EPOCH) / 3600 ))

if [ "$AGE_HOURS" -gt "$MAX_AGE_HOURS" ]; then
    send_alert "Ultimo backup tiene ${AGE_HOURS} horas (max ${MAX_AGE_HOURS}h). Tipo: ${BACKUP_TYPE}"
    exit 1
fi

log_ok "Backup ${BACKUP_TYPE} OK. Edad: ${AGE_HOURS}h."

# 4. Run integrity verification (weekly on Sundays)
DAY_OF_WEEK=$(date +%u)
if [ "$DAY_OF_WEEK" = "7" ]; then
    VERIFY_RESULT=$(pgbackrest --stanza="$STANZA" verify 2>&1) || {
        send_alert "Verificacion de integridad fallo: ${VERIFY_RESULT}"
        exit 1
    }
    log_ok "Verificacion de integridad semanal OK."
fi

exit 0
