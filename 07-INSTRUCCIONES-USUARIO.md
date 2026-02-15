# 07 - Instrucciones para el Usuario (Paso a Paso)

Este documento te dice EXACTAMENTE que hacer en cada momento. Claude no puede hacer estas cosas por ti porque requieren acceso a tu navegador, tus cuentas, o tu servidor fisico.

---

## CUANDO INICIES FASE 0: INFRAESTRUCTURA

### Paso 0.1: Contratar VPS Principal

1. Ir a uno de estos proveedores:
   - **Hetzner** (recomendado, buena relacion precio/rendimiento): https://www.hetzner.com/cloud
   - **Contabo** (mas barato pero menos estable): https://contabo.com
   - **DigitalOcean**: https://www.digitalocean.com
2. Crear cuenta
3. Contratar un VPS con estas specs MINIMAS:
   - **CPU**: 4 cores
   - **RAM**: 8 GB
   - **Disco**: 100 GB SSD
   - **SO**: Ubuntu 22.04 LTS
   - **Region**: La mas cercana a Guadalajara (USA central o Mexico si hay)
4. Anotar: IP del servidor, usuario root, contrasena
5. Darle esos datos a Claude

### Paso 0.2: Contratar VPS Secundario (Backups)

1. En el MISMO proveedor o en otro diferente
2. Specs minimas:
   - **CPU**: 2 cores
   - **RAM**: 2 GB
   - **Disco**: 200 GB HDD (no necesita SSD)
   - **SO**: Ubuntu 22.04 LTS
3. Anotar: IP, usuario root, contrasena
4. Darle esos datos a Claude

### Paso 0.3: Instalar EasyPanel

1. Conectarte al VPS principal por SSH:
   ```bash
   ssh root@TU_IP_DEL_VPS
   ```
2. Ejecutar el instalador de EasyPanel:
   ```bash
   curl -sSL https://get.easypanel.io | sh
   ```
3. Al terminar, te dira una URL como `http://TU_IP:3000`
4. Abrir esa URL en tu navegador
5. Crear tu cuenta de admin de EasyPanel
6. Darle la URL a Claude

### Paso 0.4: Registrar Dominio

1. Si ya tienes dominio, saltar al paso 0.5
2. Si no, comprar uno en:
   - **Namecheap**: https://www.namecheap.com
   - **Cloudflare**: https://www.cloudflare.com (recomendado, incluye CDN gratis)
   - **GoDaddy**: https://www.godaddy.com
3. Anotar el dominio comprado

### Paso 0.5: Configurar DNS

1. Ir al panel de tu proveedor de dominio
2. En la seccion de DNS, crear estos registros:
   ```
   Tipo A  |  api.tudominio.com  |  IP_DEL_VPS_PRINCIPAL
   Tipo A  |  app.tudominio.com  |  IP_DEL_VPS_PRINCIPAL
   Tipo A  |  wha.tudominio.com  |  IP_DEL_VPS_PRINCIPAL  (Evolution API)
   ```
3. Esperar ~15 minutos a que propaguen
4. Verificar: `ping api.tudominio.com` debe responder con la IP de tu VPS

### Paso 0.6: Crear Repositorio GitHub

1. Ir a https://github.com/new
2. Nombre: `crm-protegrt` (o el que prefieras)
3. Privado: SI
4. No inicializar con README (Claude lo hara)
5. Crear
6. Copiar la URL del repo (ej: `https://github.com/tu-usuario/crm-protegrt.git`)
7. Darsela a Claude

### Paso 0.7: Configurar WireGuard VPN

Claude te generara:
- El archivo de configuracion del servidor (`wg0.conf`)
- Los archivos de configuracion para cada dispositivo cliente
- Los comandos exactos para instalarlos

Tu deberas:
1. Conectarte al VPS por SSH
2. Copiar y pegar los comandos que Claude te de
3. Instalar la app WireGuard en tu PC/telefono:
   - Windows: https://www.wireguard.com/install/
   - Android: Play Store → WireGuard
   - iOS: App Store → WireGuard
4. Importar el archivo de configuracion que Claude genere

### Paso 0.8: Instalar Evolution API

Claude te dara los pasos para crear el servicio en EasyPanel. Tu deberas:
1. Ir al panel de EasyPanel
2. Crear un nuevo servicio
3. Pegar la configuracion que Claude te de
4. Escanear el QR de WhatsApp Business con tu telefono

---

## CUANDO INICIES FASE 1.1: MIGRACION DE EMPLEADOS EN MYSQL

### Paso 1.1: Backup de MySQL

1. Abrir una terminal en el servidor de MySQL actual
2. Ejecutar:
   ```bash
   mysqldump -u root -p --single-transaction --routines --triggers crm_seguros > backup_antes_empleados_$(date +%Y%m%d).sql
   ```
3. Verificar que el archivo se creo y tiene tamano razonable (> 1MB)

### Paso 1.2: Ejecutar Scripts de Migracion

Seguir la guia completa en: `database/migrations/GUIA_MIGRACION_EMPLEADOS.md`

Resumen rapido:
```bash
# 1. Schema (crea tablas nuevas, NO toca las viejas)
mysql -u root -p crm_seguros < database/migrations/unificar_empleados_001_schema.sql

# 2. Data (migra datos, remapea FKs) - CUIDADO: NO re-ejecutable
mysql -u root -p crm_seguros < database/migrations/unificar_empleados_002_data.sql

# 3. VERIFICAR que la app funciona antes de continuar
# Probar: login, polizas, cobranza, siniestros

# 4. Cleanup (elimina tablas viejas) - IRREVERSIBLE
mysql -u root -p crm_seguros < database/migrations/unificar_empleados_003_cleanup.sql

# 5. Roles y permisos
mysql -u root -p crm_seguros < database/migrations/004_roles_permisos.sql
```

### Paso 1.3: Desplegar Codigo Actualizado

1. En la PC donde corre la app:
   ```bash
   cd D:\pqtcreacion
   git checkout claude
   git pull
   ```
2. Reiniciar la aplicacion
3. Probar que todo funciona

---

## CUANDO INICIES FASE 4: MIGRACION MYSQL → POSTGRESQL

Claude te dara:
- Scripts de migracion completos
- Queries de verificacion post-migracion
- Plan de rollback

Tu deberas:
1. Programar una ventana de mantenimiento (fin de semana recomendado)
2. Avisar a los usuarios que el sistema estara en mantenimiento
3. Ejecutar los scripts que Claude te de
4. Correr las queries de verificacion
5. Confirmar que los datos estan correctos

---

## CUANDO INICIES FASE 5: DESPLIEGUE

Claude te dara:
- Dockerfiles para cada servicio
- Configuracion de EasyPanel (servicios, variables de entorno, volumenes)
- Comandos para desplegar

Tu deberas:
1. En EasyPanel, crear los servicios que Claude indique
2. Configurar las variables de entorno que Claude liste
3. Hacer el deploy
4. Verificar que todo funciona
5. Configurar SSL (automatico en EasyPanel)

---

## REGLA DE ORO

Siempre que Claude te diga "ejecuta esto", tu:
1. Lee el comando completo antes de ejecutarlo
2. Si no lo entiendes, pregunta
3. Si involucra borrar datos, verifica que tienes backup
4. Ejecuta
5. Copia el resultado y pegalo de vuelta a Claude

Si algo falla:
1. NO intentes arreglarlo por tu cuenta
2. Copia el error COMPLETO
3. Pegalo a Claude
4. Claude te dira como arreglarlo
