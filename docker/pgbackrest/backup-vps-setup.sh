#!/bin/bash
# =============================================================================
# Setup script for the BACKUP VPS (remote server)
# Run this ONCE on the backup VPS before starting pgBackRest.
#
# Prerequisites:
#   - Ubuntu 22.04+ or Debian 12+
#   - At least 200GB disk space
#   - SSH access from main VPS
# =============================================================================

set -euo pipefail

echo "=== Configurando VPS de backup para pgBackRest ==="

# 1. Install pgBackRest
apt-get update && apt-get install -y pgbackrest

# 2. Create pgbackrest user (restricted shell)
if ! id "pgbackrest" &>/dev/null; then
    useradd -m -s /bin/bash pgbackrest
    echo "Usuario pgbackrest creado"
fi

# 3. Create directories
mkdir -p /var/lib/pgbackrest
mkdir -p /var/log/pgbackrest
chown -R pgbackrest:pgbackrest /var/lib/pgbackrest /var/log/pgbackrest

# 4. Setup SSH key directory
mkdir -p /home/pgbackrest/.ssh
chmod 700 /home/pgbackrest/.ssh
chown pgbackrest:pgbackrest /home/pgbackrest/.ssh

echo ""
echo "=== PASOS MANUALES RESTANTES ==="
echo ""
echo "1. En el VPS PRINCIPAL, generar clave SSH:"
echo "   ssh-keygen -t ed25519 -f /root/.ssh/pgbackrest_key -N '' -C 'pgbackrest@protegrt'"
echo ""
echo "2. Copiar la clave publica al VPS de backup:"
echo "   ssh-copy-id -i /root/.ssh/pgbackrest_key.pub pgbackrest@<BACKUP_VPS_IP>"
echo ""
echo "3. En el VPS PRINCIPAL, crear la configuracion pgBackRest:"
echo "   cp pgbackrest.conf /etc/pgbackrest/pgbackrest.conf"
echo "   # Editar con los valores reales de BACKUP_VPS_HOST y PGBACKREST_CIPHER_PASS"
echo ""
echo "4. Inicializar el stanza:"
echo "   pgbackrest --stanza=protegrt stanza-create"
echo ""
echo "5. Verificar la configuracion:"
echo "   pgbackrest --stanza=protegrt check"
echo ""
echo "6. Ejecutar el primer backup completo:"
echo "   pgbackrest --stanza=protegrt backup --type=full"
echo ""
echo "=== Setup del VPS de backup completado ==="
