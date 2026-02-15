# 04 - Plan de Seguridad, Despliegue y Migracion de Datos

**Proyecto:** CRM Protegrt - Nuevo Sistema
**Fecha:** 2026-02-14
**Autor:** Agente de Seguridad y Despliegue
**Version:** 1.0

> **NOTA:** Las decisiones tecnicas canonicas estan en `CLAUDE.md` seccion "Decisiones Canonicas v1".
> En caso de contradiccion entre este documento y CLAUDE.md, CLAUDE.md prevalece.

---

## INDICE

1. [Plan de Seguridad Completo](#1-plan-de-seguridad-completo)
2. [Despliegue en EasyPanel](#2-despliegue-en-easypanel)
3. [Backup de PostgreSQL](#3-backup-de-postgresql)
4. [Migracion de Datos MySQL a PostgreSQL](#4-migracion-de-datos-mysql-a-postgresql)

---

## 1. PLAN DE SEGURIDAD COMPLETO

### CONTEXTO CRITICO

El sistema actual (desktop PyQt5 en LAN) tiene **13 hallazgos criticos de seguridad** documentados en INFORME_OPTIMIZACION.md:
- Credenciales de BD en historial git (S1)
- API Keys en texto plano (S2, S5)
- Tokens de Telegram hardcodeados (S3, S4)
- JWT SECRET_KEY predecible y hardcodeada (S6)
- Verificacion de expiracion JWT deshabilitada (S9)
- SSL deshabilitado en conexion MySQL (S15)
- Dashboard accesible sin login (S16)

**El nuevo sistema estara en INTERNET.** No se puede cometer NINGUN error de seguridad. Cada vulnerabilidad del sistema actual debe tener una contramedida explicita.

---

### 1.1 Autenticacion

#### 1.1.1 JWT con Access + Refresh Tokens

```
Arquitectura de tokens:

  Access Token (corta vida)          Refresh Token (larga vida)
  +---------------------------+      +---------------------------+
  | Header: RS256             |      | UUID v4 opaco             |
  | Payload:                  |      | Almacenado en Redis:      |
  |   sub: user_id            |      |   key: token_uuid         |
  |   role: "gerente"         |      |   value: {                |
  |   permissions: [...]      |      |     user_id, device_id,   |
  |   device_type: "web"      |      |     family, created_at,   |
  |   iat: timestamp          |      |     expires_at            |
  |   exp: +15 minutos        |      |   }                       |
  | Firma: RSA-SHA256         |      | Cookie: httpOnly+Secure   |
  +---------------------------+      | TTL: 7d web / 30d movil   |
                                     +---------------------------+
```

**Reglas:**
- Access token: JWT RS256, vida de 15 minutos, se envia en header `Authorization: Bearer <token>`
- Refresh token: UUID opaco almacenado en Redis, vida de 7 dias (web) / 30 dias (movil), se almacena en cookie httpOnly secure SameSite=Strict
- Al expirar el access token, el frontend llama `POST /api/v1/auth/refresh` con el refresh token (UUID)
- Refresh token rotation: cada uso genera un nuevo UUID e invalida el anterior en Redis
- Si se detecta reuso de un refresh token ya rotado, se invalidan TODOS los tokens de esa familia en Redis (posible robo)

**Nota sobre RS256 (algoritmo asimetrico):**
- RS256 usa claves asimetricas: una clave privada para firmar y una clave publica para verificar
- La clave privada permanece UNICAMENTE en el servidor API (nunca se distribuye)
- La clave publica puede distribuirse a cualquier servicio que necesite verificar tokens (microservicios, gateways, etc.)
- Ventaja sobre HS256: si un servicio solo necesita verificar tokens, solo necesita la clave publica; comprometer ese servicio no permite firmar tokens falsos

**Contramedida vs sistema actual:**
- S6: Se usaran claves RSA de 2048 bits minimo, la clave privada almacenada UNICAMENTE en variable de entorno del servidor API
- S9: `verify_exp` SIEMPRE habilitado. Sin excepciones

#### 1.1.2 Almacenamiento Seguro de Tokens

| Cliente | Access Token | Refresh Token |
|---------|-------------|---------------|
| Web Admin (React) | En memoria (variable JS, NO localStorage) | Cookie httpOnly + Secure + SameSite=Strict |
| App Cobrador (React Native) | SecureStore (iOS Keychain / Android Keystore) | SecureStore |
| App Vendedor (React Native) | SecureStore | SecureStore |
| App Ajustador (React Native) | SecureStore | SecureStore |

**Por que NO localStorage para access tokens en web:**
- localStorage es accesible via JavaScript, vulnerable a XSS
- Si un atacante inyecta JS, puede leer el token
- En memoria se pierde al cerrar pestana (fuerza re-auth, que es correcto)

#### 1.1.3 Sesiones por Dispositivo

La tabla `device_session` del schema PostgreSQL ya soporta esto:

```
Un usuario puede tener sesiones activas en:
  - 1 sesion web admin
  - 1 sesion app cobrador (Android/iOS)
  - 1 sesion app vendedor (Android/iOS)
  - 1 sesion app ajustador (Android/iOS)
```

**Implementacion:**
- Al hacer login, se crea/actualiza `device_session` con `device_id`, `device_type`, `app_type`
- Si ya existe sesion activa para ese `(user_id, app_type)`, se invalida la anterior
- Esto previene compartir cuentas entre multiples dispositivos del mismo tipo

#### 1.1.4 Logout Remoto / Invalidacion de Sesiones

```
Endpoints:
  POST /api/v1/auth/logout              -> Invalida sesion actual
  POST /api/v1/auth/logout-all          -> Invalida TODAS las sesiones del usuario
  POST /api/v1/auth/logout-device/{id}  -> Invalida sesion de un dispositivo especifico
  GET  /api/v1/auth/sessions            -> Lista sesiones activas del usuario
```

**Implementacion:**
- Blacklist de tokens en Redis con TTL igual a la vida restante del token
- Al verificar un access token, se consulta Redis para ver si esta en blacklist
- Complejidad O(1) por consulta

#### 1.1.5 2FA para Admin/Gerentes

- Implementar TOTP (Time-based One-Time Password) compatible con Google Authenticator / Authy
- Obligatorio para: rol `admin`, rol `gerente` (cualquier departamento)
- Opcional para: otros roles
- Flujo: login con usuario/contrasena -> si 2FA habilitado -> pedir codigo TOTP -> generar tokens
- Backup codes: 10 codigos de un solo uso generados al activar 2FA

#### 1.1.7 Politica de "Recordar Sesion"

**NO se implementa funcionalidad de "Recordar sesion" / "Remember me" en la aplicacion web.**

**Justificacion:**
- Las computadoras de la oficina son compartidas por multiples personas
- No es seguro mantener sesiones persistentes en equipos compartidos

**Comportamiento en Web (React Admin):**
- El access token se almacena UNICAMENTE en memoria (variable JavaScript)
- Al cerrar el navegador o la pestana, el access token en memoria se pierde
- El refresh token en cookie httpOnly se mantiene hasta 7 dias en el navegador
- Sin embargo, al cerrar la pestana, el access token en memoria se pierde y el usuario debe re-autenticarse via el refresh token al reabrir la aplicacion
- Si el refresh token tambien ha expirado o fue invalidado, el usuario debe hacer login completo nuevamente

**Comportamiento en Apps Moviles (React Native):**
- La sesion persiste normalmente via SecureStore (iOS Keychain / Android Keystore)
- Los dispositivos moviles son personales, no compartidos
- El refresh token se almacena en SecureStore y se usa para renovar el access token automaticamente

#### 1.1.8 Restriccion de Acceso por Red

**Opcion preferida: VPN (WireGuard)**

El acceso al sistema web se restringe via VPN WireGuard:

```
Internet                    Red VPN WireGuard              Servidor API
+----------+               +------------------+           +-----------+
| Empleado |--[WireGuard]->| Red interna VPN  |---------->| API       |
| remoto   |               | 10.0.0.0/24      |           | (acepta   |
+----------+               +------------------+           |  solo VPN)|
                                    ^                      +-----------+
+----------+               |        |
| Empleado |--[Red local]--+
| oficina  | (VPN automatica)
+----------+
```

- El servidor API solo acepta conexiones desde la red VPN (firewall a nivel de red)
- Los empleados en la oficina se conectan automaticamente a la VPN via la red local
- Los empleados remotos se conectan manualmente al VPN WireGuard desde su dispositivo
- **Admins estan EXENTOS de todas las restricciones de red** (pueden acceder desde cualquier IP)
- WireGuard es ligero, rapido, y facil de configurar en EasyPanel

**Opcion alternativa (fallback): Geofencing + Horarios**

Si no se implementa VPN, se usa geofencing + restriccion por horario laboral como alternativa:

- **Geolocalizacion:** La ubicacion del dispositivo se compara contra un poligono definido de la oficina + radio de tolerancia configurable
- **Horario laboral:** Solo se permite acceso en horario laboral (configurable por administradores, ej. Lunes-Viernes 8:00-18:00, Sabado 9:00-14:00)
- **Permisos especiales:** Acceso fuera de horario puede concederse individualmente via `empleado_permiso_override` (campo `concedido=1` para el permiso `acceso_fuera_horario`)
- **Admins estan EXENTOS de restricciones de horario y ubicacion**

#### 1.1.6 Proteccion contra Brute Force

```python
# Rate limiting en login (FastAPI + Redis)
RATE_LIMITS = {
    "login": {
        "por_ip": "10 intentos / 15 minutos",
        "por_usuario": "5 intentos / 15 minutos",
        "bloqueo_cuenta": "10 intentos fallidos -> bloqueo 30 minutos",
        "alerta": "5 intentos fallidos -> notificacion Telegram a admin"
    },
    "refresh": {
        "por_ip": "30 / 15 minutos"
    },
    "password_reset": {
        "por_email": "3 / hora",
        "por_ip": "5 / hora"
    }
}
```

**Implementacion tecnica:**
- Usar `slowapi` (wrapper de `limits` para FastAPI) con backend Redis
- Contador de intentos fallidos por usuario en Redis con TTL de 15 minutos
- Al alcanzar 10 intentos, SET `locked:{user_id}` con TTL 1800 segundos
- Log de TODOS los intentos de login (exitosos y fallidos) en `audit_log`

---

### 1.2 Autorizacion

#### 1.2.1 RBAC con Permisos Granulares

**Roles predefinidos y sus permisos:**

```
ADMIN
  -> * (todos los permisos)

GERENTE (per department - via empleado_departamentos.es_gerente)
  -> Todos los permisos de su(s) departamento(s)
  -> employees.read, employees.write (de su departamento)
  -> proposals.approve, proposals.reject (de su departamento)
  -> reports.* (de su departamento)
  -> dashboard.* (de su departamento)
  -> rh.access (si es gerente de RH)

AUXILIAR
  -> policies.create, policies.read
  -> clients.create, clients.read, clients.update
  -> payments.read
  -> vacaciones.read, vacaciones.write (solicitar propias)

COBRADOR (app movil - flag es_cobrador en empleado)
  -> proposals.create, proposals.read_own
  -> receipts.read_assigned, receipts.use
  -> clients.read_assigned
  -> collections.read_own_route

VENDEDOR (app movil - flag es_vendedor en empleado)
  -> policies.create, policies.read_own
  -> clients.create, clients.read
  -> quotes.create, quotes.read_own
  -> renewals.read_assigned

AJUSTADOR (app movil - flag es_ajustador en empleado)
  -> incidents.read_assigned, incidents.update_own
  -> tow_services.read_assigned, tow_services.update_own
  -> shifts.read_current
```

**Empleados con multiples roles de negocio:**
- Un empleado puede tener multiples roles de negocio simultaneamente (es_vendedor=1, es_cobrador=1, es_ajustador=1)
- Los permisos se calculan como: `permisos_del_rol_sistema UNION permisos_por_flags_de_negocio UNION overrides_individuales`
- La tabla `empleado_permiso_override` permite conceder (`concedido=1`) o revocar (`concedido=0`) permisos individuales a un empleado especifico, independientemente de su rol

#### 1.2.2 Middleware de Autorizacion

```python
# Cada endpoint DEBE tener decorador de permisos
@router.get("/policies/{id}")
async def get_policy(
    id: int,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("policies.read"))
):
    ...

@router.post("/proposals")
async def create_proposal(
    data: ProposalCreate,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission("proposals.create"))
):
    ...
```

**Regla absoluta:** NINGUN endpoint sin verificacion de permisos. Contramedida directa contra S16 (dashboard accesible sin login).

#### 1.2.3 Permisos por Modulo y Accion

Formato: `modulo.accion`

| Modulo | Acciones |
|--------|----------|
| policies | create, read, read_own, update, delete, change_seller |
| clients | create, read, read_assigned, update, delete |
| payments | create, read, update, reverse |
| proposals | create, read_own, approve, reject |
| collections | read, read_own_route, assign, reassign |
| receipts | create_batch, assign, read_assigned, use, cancel |
| incidents | create, read, read_assigned, update_own, close |
| tow_services | create, read, read_assigned, update_own |
| endorsements | create, read, approve, reject, apply |
| cancellations | create, read, undo |
| renewals | create, read, read_assigned |
| promotions | create, read, update, apply |
| quotes | create, read, read_own, approve |
| users | create, read, update, delete, admin |
| employees | create, read, write, toggle_status |
| rh | access, approve_vacaciones |
| vacaciones | read, write, approve |
| reports | view, export |
| dashboard | view, collection |
| notifications | send, read |

---

### 1.3 Proteccion contra OWASP Top 10 (2021)

#### A01:2021 - Broken Access Control

**Como aplica al CRM:**
- Cobrador accediendo a pagos de otros cobradores
- Vendedor viendo polizas de otros vendedores
- Usuario sin rol admin accediendo a panel de administracion

**Prevencion:**
1. Verificar permisos en CADA endpoint (middleware `require_permission`)
2. Filtro de propiedad: endpoints `_own` solo retornan recursos del usuario actual
3. CORS estricto (solo dominios autorizados)
4. Denegar por defecto: si no tiene permiso explicito, se rechaza

**Implementacion:**
```python
# Filtro de propiedad en queries
async def get_own_proposals(user: User, db: AsyncSession):
    query = select(PaymentProposal).where(
        PaymentProposal.submitted_by_user_id == user.id
    )
    return await db.execute(query)
```

#### A02:2021 - Cryptographic Failures

**Como aplica al CRM:**
- S1-S6: Credenciales en texto plano en codigo/git
- S15: Conexiones BD sin SSL
- Datos PII: nombres, telefonos, emails, RFC de clientes

**Prevencion:**
1. TLS 1.3 en todas las conexiones (API, BD, Redis)
2. Passwords hasheados con Argon2id (bcrypt como fallback para passwords migrados)
3. Secrets en variables de entorno, NUNCA en codigo
4. Datos PII sensibles encriptados en reposo con pgcrypto
5. JWT con RS256 (claves RSA asimetricas), rotacion semestral de claves

**Implementacion:**
```python
# Hashing de passwords
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

# Datos PII en PostgreSQL
# RFC y datos fiscales encriptados con pgcrypto
# INSERT INTO client (rfc_encrypted) VALUES (pgp_sym_encrypt($1, $2))
# SELECT pgp_sym_decrypt(rfc_encrypted, $1) FROM client WHERE id = $2
```

#### A03:2021 - Injection

**Como aplica al CRM:**
- S11-S14: f-strings en queries SQL (system actual)
- S13: Claves de diccionario interpoladas en SQL

**Prevencion:**
1. ORM (SQLAlchemy) para TODAS las queries - nunca SQL crudo
2. Si es necesario SQL crudo, SIEMPRE parameterized queries
3. Input validation con Pydantic en cada endpoint
4. Sanitizacion de inputs en busquedas de texto

**Implementacion:**
```python
# CORRECTO - SQLAlchemy ORM
result = await db.execute(
    select(Policy).where(Policy.folio == folio_param)
)

# CORRECTO - Parameterized si es necesario SQL crudo
result = await db.execute(
    text("SELECT * FROM policy WHERE folio = :folio"),
    {"folio": folio_param}
)

# PROHIBIDO - NUNCA hacer esto
# result = await db.execute(f"SELECT * FROM policy WHERE folio = {folio}")
```

#### A04:2021 - Insecure Design

**Como aplica al CRM:**
- Sistema actual sin separacion de capas (SQL en vistas)
- Sin validacion de logica de negocio en backend

**Prevencion:**
1. Arquitectura estricta: Router -> Service -> Repository -> DB
2. Validacion de negocio en capa Service (no en router ni en frontend)
3. Threat modeling previo al desarrollo de cada modulo
4. Tests de seguridad automatizados en CI/CD

#### A05:2021 - Security Misconfiguration

**Como aplica al CRM:**
- S6: SECRET_KEY predecible
- S15: SSL deshabilitado
- S16: Acceso sin autenticacion

**Prevencion:**
1. Headers de seguridad en TODAS las respuestas (ver 1.5.5)
2. Deshabilitar endpoints de debug/docs en produccion
3. Configuracion diferenciada staging vs produccion
4. Escaneo periodico de vulnerabilidades (Trivy para contenedores)

#### A06:2021 - Vulnerable and Outdated Components

**Prevencion:**
1. Dependabot o Renovate habilitado en GitHub
2. `pip audit` en pipeline CI/CD (falla si hay vulnerabilidades criticas)
3. Imagenes Docker base con tags fijos (no `latest`)
4. Actualizacion mensual de dependencias

#### A07:2021 - Identification and Authentication Failures

**Como aplica al CRM:**
- S6: JWT debil
- S9: Tokens que nunca expiran
- S10: Extension infinita de sesion

**Prevencion:**
1. Tokens con expiracion estricta (15 min access, 7 dias refresh)
2. Refresh token rotation con deteccion de reuso
3. Bloqueo de cuenta tras intentos fallidos
4. Passwords fuertes obligatorios (min 8 chars, 1 mayuscula, 1 numero)

#### A08:2021 - Software and Data Integrity Failures

**Prevencion:**
1. CI/CD con verificacion de integridad de dependencias (hash checking)
2. Signed commits en rama principal
3. Branch protection rules en GitHub (requiere review + checks pass)
4. Docker images firmadas

#### A09:2021 - Security Logging and Monitoring Failures

**Como aplica al CRM:**
- Sistema actual sin logging de seguridad
- Sin auditoria de acciones

**Prevencion:**
1. Log de TODOS los eventos de autenticacion (login, logout, fallos, 2FA)
2. Log de TODAS las acciones de modificacion (CREATE, UPDATE, DELETE)
3. Audit trail via triggers de PostgreSQL (tabla `audit_log` particionada)
4. Alertas en tiempo real para eventos sospechosos (Telegram a admin)
5. Retencion de logs: 90 dias en caliente, 1 anio en frio

**Eventos que generan alerta inmediata:**
```
- 5+ intentos de login fallidos en 5 minutos
- Login desde IP/pais no habitual
- Acceso a endpoint admin desde IP no autorizada
- Reuso de refresh token (posible robo de sesion)
- Error 403 masivo desde un mismo usuario (posible enumeracion)
- Cambio de password o email de usuario admin
```

#### A10:2021 - Server-Side Request Forgery (SSRF)

**Como aplica al CRM:**
- Integracion con API de cotizaciones externa
- Integracion con Evolution API (WhatsApp)
- Integracion con Telegram Bot API

**Prevencion:**
1. Validar que URLs de integracion apunten SOLO a dominios autorizados
2. No permitir URLs proporcionadas por usuario como destino de requests del servidor
3. Bloquear acceso a metadatos de cloud (169.254.169.254)
4. Separar red de contenedores (ver seccion 2.1.3)

---

### 1.4 Datos Sensibles

#### 1.4.1 Encriptacion en Transito

- TLS 1.3 obligatorio en TODAS las conexiones externas
- Certificados Let's Encrypt con renovacion automatica (ver 2.4)
- Conexion PostgreSQL: `sslmode=require` (contramedida directa vs S15)
- Conexion Redis: TLS habilitado o red interna Docker unicamente

#### 1.4.2 Encriptacion en Reposo

**Datos que requieren encriptacion con pgcrypto:**

| Dato | Tabla | Campo | Metodo |
|------|-------|-------|--------|
| RFC del cliente | client | rfc_encrypted | pgp_sym_encrypt |
| Tokens de Telegram | configuracion | encrypted_value | pgp_sym_encrypt |
| API Keys de terceros | configuracion | encrypted_value | pgp_sym_encrypt |

**Datos que NO requieren encriptacion en reposo** (ya estan protegidos por acceso BD):
- Nombres, telefonos, emails (son datos operativos necesarios en queries)
- Montos de pagos, folios (datos de negocio)

La clave de encriptacion de pgcrypto se almacena en variable de entorno `PG_ENCRYPTION_KEY`, NUNCA en la BD.

#### 1.4.3 Hashing de Passwords

```python
# Argon2id (preferido) o bcrypt como fallback
# Argon2id es resistente a ataques GPU y side-channel
from argon2 import PasswordHasher
ph = PasswordHasher(
    time_cost=3,        # Iteraciones
    memory_cost=65536,  # 64MB de RAM
    parallelism=4,      # 4 hilos
    hash_len=32,        # 256 bits de output
    salt_len=16         # 128 bits de salt
)

# Hash al crear/cambiar password
hash = ph.hash(password)

# Verificar al login
try:
    ph.verify(stored_hash, password)
    if ph.check_needs_rehash(stored_hash):
        # Re-hash con parametros actualizados
        new_hash = ph.hash(password)
        update_user_hash(user_id, new_hash)
except VerifyMismatchError:
    raise InvalidCredentials()
```

#### 1.4.4 Manejo de Secrets

**Regla absoluta:** NINGUN secret en codigo fuente, archivos de configuracion, ni repositorio git.

```
Jerarquia de secrets (de mas seguro a menos):

1. Variables de entorno en EasyPanel (produccion)
   -> DATABASE_URL, JWT_SECRET, PG_ENCRYPTION_KEY, etc.

2. Archivo .env local (desarrollo)
   -> .env en .gitignore (NUNCA commiteado)
   -> .env.example con valores placeholder en repositorio

3. NUNCA:
   -> Hardcodeado en codigo (como S3, S5, S6 del sistema actual)
   -> En archivos de configuracion commiteados (como S1, S2)
   -> En historial git (limpiar con BFG antes de publicar)
```

**Variables de entorno requeridas:**

```bash
# Base de datos
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/protegrt_db
DATABASE_URL_QUOTES=postgresql+asyncpg://user:pass@host:5432/cotizaciones_db

# Seguridad
JWT_PRIVATE_KEY_PATH=<ruta a clave privada RSA para firmar tokens RS256>
JWT_PUBLIC_KEY_PATH=<ruta a clave publica RSA para verificar tokens RS256>
PG_ENCRYPTION_KEY=<hex 64 chars para pgcrypto>

# Redis
REDIS_URL=redis://redis:6379/0

# Integraciones
EVOLUTION_API_URL=https://app-evolution-api.host
EVOLUTION_API_KEY=<api key>
EVOLUTION_INSTANCE=cobranza
TELEGRAM_BOT_TOKEN=<token>
TELEGRAM_RENOVA_BOT_TOKEN=<token>
QUOTES_API_URL=https://cotizaciones.protegrt.com
QUOTES_API_KEY=<api key>
FILES_API_URL=https://archivos.protegrt.com
FILES_API_KEY=<api key>

# Configuracion
ENVIRONMENT=production  # production | staging | development
CORS_ORIGINS=https://app.protegrt.com,https://admin.protegrt.com
SENTRY_DSN=<dsn para error tracking>
```

#### 1.4.5 Compliance con LFPDPPP (Mexico)

La Ley Federal de Proteccion de Datos Personales en Posesion de los Particulares (LFPDPPP) aplica al CRM porque maneja:
- Nombres, telefonos, emails, direcciones de clientes
- RFC (dato fiscal sensible)
- Datos de vehiculos (placas, serie)

**Medidas de cumplimiento:**
1. Aviso de privacidad: informar al cliente que datos se recopilan y para que
2. Consentimiento: registro de consentimiento del cliente
3. Acceso: endpoint para que el cliente consulte sus datos
4. Rectificacion: endpoint para que el cliente corrija sus datos
5. Cancelacion: soft delete con retencion minima legal
6. Oposicion: mecanismo para oponerse al uso de datos para fines secundarios
7. Oficial de privacidad: designar responsable del tratamiento de datos

---

### 1.5 Seguridad de API

#### 1.5.1 Rate Limiting

```python
# Limites por endpoint y por usuario
RATE_LIMITS = {
    # Autenticacion (estricto)
    "/auth/login":         "10/15min por IP, 5/15min por usuario",
    "/auth/refresh":       "30/15min por IP",
    "/auth/reset-password": "3/hora por email",

    # Lectura (moderado)
    "/policies":           "100/min por usuario",
    "/payments":           "100/min por usuario",
    "/clients":            "100/min por usuario",

    # Escritura (conservador)
    "/proposals":          "30/min por usuario",
    "/policies (POST)":    "10/min por usuario",

    # Busquedas (para prevenir scraping)
    "/search/*":           "30/min por usuario",

    # Notificaciones (muy conservador)
    "/notifications/send": "10/min por usuario",

    # Global
    "default":             "200/min por usuario, 1000/min por IP"
}
```

#### 1.5.2 CORS

```python
# FastAPI CORS - configuracion estricta
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "https://app.protegrt.com",      # Frontend web principal
    "https://admin.protegrt.com",    # Panel admin (si es diferente)
]

# En desarrollo, agregar localhost
if ENVIRONMENT == "development":
    ALLOWED_ORIGINS.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # NO usar ["*"] en produccion
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,  # Cache preflight 10 minutos
)
```

#### 1.5.3 Input Validation

```python
# Pydantic schemas para CADA endpoint
from pydantic import BaseModel, Field, validator
import re

class PolicyCreate(BaseModel):
    client_id: int = Field(gt=0)
    coverage_id: int = Field(gt=0)
    seller_id: int = Field(gt=0)
    contract_folio: int = Field(gt=0)
    effective_date: date
    payment_plan: PaymentPlanType
    vehicle: VehicleCreate

    @validator("contract_folio")
    def validate_contract_folio(cls, v):
        if v < 1 or v > 999999:
            raise ValueError("Folio de contrato fuera de rango")
        return v

class ProposalCreate(BaseModel):
    original_payment_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    payment_method: PaymentMethodType
    receipt_number: str = Field(regex=r"^[A-Z]\d{4}$")  # Formato: A0001
    latitude: Optional[float] = Field(ge=-90, le=90)
    longitude: Optional[float] = Field(ge=-180, le=180)
```

#### 1.5.4 Proteccion contra Inyeccion SQL

- ORM SQLAlchemy para el 100% de las queries
- Linter personalizado en CI/CD que detecte `f"SELECT` o `f"INSERT` o `f"UPDATE` y falle el build
- Code review obligatorio para cualquier uso de `text()` en SQLAlchemy

#### 1.5.5 Headers de Seguridad

```python
# Middleware de headers de seguridad
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "0"  # Deshabilitado (CSP es mejor)
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(self)"
    # Remover headers que exponen informacion del servidor
    response.headers.pop("server", None)
    response.headers.pop("x-powered-by", None)
    return response
```

#### 1.5.6 Logging de Seguridad y Auditoria

**Eventos que se registran:**

| Evento | Nivel | Destino |
|--------|-------|---------|
| Login exitoso | INFO | audit_log + archivo |
| Login fallido | WARN | audit_log + archivo + alerta si >5 |
| Creacion de poliza | INFO | audit_log (trigger PG) |
| Modificacion de pago | INFO | audit_log (trigger PG) |
| Cancelacion de poliza | INFO | audit_log (trigger PG) |
| Cambio de permisos/roles | WARN | audit_log + archivo + alerta |
| Intento de acceso no autorizado (403) | WARN | archivo + alerta si masivo |
| Error interno (500) | ERROR | archivo + Sentry + alerta |
| Reuso de refresh token | CRITICAL | archivo + alerta inmediata |

**Formato de log:**
```json
{
  "timestamp": "2026-02-14T10:30:00Z",
  "level": "INFO",
  "event": "auth.login.success",
  "user_id": 42,
  "ip": "189.203.x.x",
  "user_agent": "Mozilla/5.0...",
  "device_type": "web",
  "request_id": "uuid-trace"
}
```

---

## 2. DESPLIEGUE EN EASYPANEL

### 2.1 Arquitectura de Contenedores

#### 2.1.1 Servicios

```
EasyPanel VPS Principal
+---------------------------------------------------------------+
|                                                                 |
|  +-------------------+     +-------------------+               |
|  |   Traefik         |     |   Backend API     |               |
|  |   (Reverse Proxy) |---->|   (FastAPI)       |               |
|  |   Puerto 80/443   |     |   Puerto 8000     |               |
|  |   SSL auto        |     |   3 workers       |               |
|  +-------------------+     +---+-------+-------+               |
|          |                     |       |                        |
|          |              +------+   +---+--------+              |
|          |              |          |             |              |
|  +-------v-------+  +--v---+  +--v-------+  +--v-----------+  |
|  | Frontend Web   |  | PG   |  | Redis    |  | Worker       |  |
|  | (Next.js/Nginx)|  | SQL  |  | Cache +  |  | (Celery/ARQ) |  |
|  | Puerto 3000    |  | 5432 |  | Sessions |  | Background   |  |
|  +-----------------+  +------+  | 6379     |  | tasks        |  |
|                                 +----------+  +--------------+  |
+---------------------------------------------------------------+
```

#### 2.1.2 Docker Compose (EasyPanel compatible)

```yaml
version: "3.8"

services:
  # --- Base de datos ---
  postgres:
    image: postgis/postgis:16-3.4
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: protegrt_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"  # Solo accesible internamente
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d protegrt_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    command: >
      postgres
        -c ssl=on
        -c ssl_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
        -c ssl_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
        -c shared_preload_libraries='pg_cron'
        -c max_connections=100
        -c shared_buffers=256MB
        -c effective_cache_size=768MB
        -c work_mem=4MB
        -c maintenance_work_mem=128MB
        -c wal_level=replica
        -c archive_mode=on
        -c archive_command='test ! -f /backups/wal/%f && cp %p /backups/wal/%f'

  # --- Cache y sesiones ---
  redis:
    image: redis:7-alpine
    restart: always
    command: >
      redis-server
        --maxmemory 128mb
        --maxmemory-policy allkeys-lru
        --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # --- Backend API ---
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/protegrt_db
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      JWT_REFRESH_SECRET_KEY: ${JWT_REFRESH_SECRET_KEY}
      ENVIRONMENT: production
      CORS_ORIGINS: ${CORS_ORIGINS}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # --- Worker para tareas en background ---
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    command: ["celery", "-A", "app.tasks", "worker", "-l", "info", "-c", "4"]
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/protegrt_db
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # --- Frontend ---
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    environment:
      NEXT_PUBLIC_API_URL: https://api.protegrt.com

volumes:
  postgres_data:
  redis_data:
```

#### 2.1.3 Networking

```
Red Docker interna (bridge):
  - postgres: solo accesible por backend y worker
  - redis: solo accesible por backend y worker
  - backend: expuesto via Traefik
  - frontend: expuesto via Traefik

NUNCA exponer postgres o redis directamente a internet.
Solo Traefik (puertos 80/443) es accesible desde internet.
```

#### 2.1.4 Volumenes Persistentes

| Volumen | Contenido | Backup |
|---------|-----------|--------|
| postgres_data | Datos PostgreSQL + WAL | Si (ver seccion 3) |
| redis_data | Cache (no critico) | No |
| uploads | Imagenes de contratos | Si (rsync diario) |

---

### 2.2 CI/CD

#### 2.2.1 Pipeline desde GitHub

```yaml
# .github/workflows/deploy.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  # 1. Lint y type-check
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff mypy
      - run: ruff check backend/
      - run: mypy backend/ --strict
      # Detectar SQL crudo en codigo
      - run: |
          if grep -rn 'f"SELECT\|f"INSERT\|f"UPDATE\|f"DELETE' backend/app/; then
            echo "ERROR: SQL crudo detectado. Usar SQLAlchemy ORM."
            exit 1
          fi

  # 2. Tests
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:16-3.4
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: protegrt_test
        ports: ["5432:5432"]
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r backend/requirements.txt
      - run: pip install pytest pytest-asyncio httpx
      - run: pytest backend/tests/ -v --cov=backend/app --cov-fail-under=60
      - run: pip audit  # Verificar vulnerabilidades en dependencias

  # 3. Build Docker image
  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/staging'
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t protegrt-backend:${{ github.sha }} backend/
      - run: docker build -t protegrt-frontend:${{ github.sha }} frontend/
      # Push to container registry

  # 4. Deploy
  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    steps:
      - run: ssh $STAGING_SERVER "cd /app && docker compose pull && docker compose up -d"

  deploy-production:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production  # Requiere aprobacion manual
    steps:
      - run: ssh $PRODUCTION_SERVER "cd /app && docker compose pull && docker compose up -d"
```

#### 2.2.2 Staging vs Production

| Aspecto | Staging | Production |
|---------|---------|------------|
| Dominio | staging.protegrt.com | app.protegrt.com |
| BD | protegrt_staging | protegrt_db |
| Datos | Copia anonimizada | Reales |
| Deploy | Automatico en push a `staging` | Manual (requiere aprobacion) |
| Logs | Verbose (DEBUG) | INFO+ |
| Rate limits | Relajados (x10) | Estrictos |
| 2FA | Deshabilitado | Habilitado |
| Sentry | Staging project | Production project |

#### 2.2.3 Rollback Strategy

```bash
# Rollback inmediato: revertir al tag anterior
docker compose pull protegrt-backend:previous-tag
docker compose up -d backend

# Rollback de BD: solo si la migracion de Alembic fallo
alembic downgrade -1

# Rollback completo: restaurar snapshot de EasyPanel
# EasyPanel soporta snapshots de volumenes
```

---

### 2.3 Monitoreo

#### 2.3.1 Health Checks

```python
# backend/app/health.py
@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    checks = {}
    # PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception:
        checks["postgres"] = "error"

    # Redis
    try:
        await redis.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"

    status = "healthy" if all(v == "ok" for v in checks.values()) else "degraded"
    code = 200 if status == "healthy" else 503
    return JSONResponse({"status": status, "checks": checks}, status_code=code)
```

#### 2.3.2 Logging Centralizado

```
Estructura de logs:

backend/
  logs/
    app.log        -> Logs de aplicacion (rotacion diaria, 30 dias)
    access.log     -> Logs de acceso HTTP (rotacion diaria, 30 dias)
    security.log   -> Eventos de seguridad (rotacion diaria, 90 dias)
    error.log      -> Solo errores (rotacion diaria, 90 dias)

Formato: JSON structurado (para parsing automatico)
Destino: stdout (para Docker logs) + archivo persistente
```

#### 2.3.3 Alertas

| Alerta | Canal | Condicion |
|--------|-------|-----------|
| Servicio caido | Telegram (grupo admin) | Health check falla 3 veces |
| Error rate > 5% | Telegram + Sentry | Mas de 5% respuestas 5xx en 5 min |
| CPU > 90% | Telegram | Sostenido por 5 minutos |
| Disco > 85% | Telegram | Volumenes postgres/uploads |
| Brute force detectado | Telegram | 10+ login fallidos desde misma IP |
| Backup fallido | Telegram + Email | Script de backup retorna error |
| SSL proximo a expirar | Telegram | 7 dias antes de expiracion |
| BD sin conexiones | Telegram | Pool de conexiones agotado |

#### 2.3.4 Metricas de Rendimiento

- Tiempo de respuesta por endpoint (P50, P95, P99)
- Queries lentas (> 500ms) logueadas automaticamente
- Uso de memoria Redis
- Pool de conexiones PostgreSQL (activas/idle/max)
- Tasa de cache hit/miss en Redis

---

### 2.4 SSL/TLS

#### 2.4.1 Certificados Automaticos

EasyPanel integra Traefik con Let's Encrypt automaticamente. Configuracion:

```
Dominios requeridos:
  - api.protegrt.com       -> Backend FastAPI
  - app.protegrt.com       -> Frontend React/Next.js
  - staging.protegrt.com   -> Staging environment
```

#### 2.4.2 Configuracion TLS

```
Protocolo minimo: TLS 1.2 (TLS 1.3 preferido)
Cipher suites: Solo AEAD (AES-GCM, ChaCha20-Poly1305)
HSTS: max-age=31536000; includeSubDomains; preload
OCSP Stapling: habilitado
```

---

## 3. BACKUP DE POSTGRESQL

### 3.1 Estrategia de Backup

#### 3.1.1 Arquitectura

```
VPS Principal (EasyPanel)              VPS Backup (separado)
+---------------------------+          +---------------------------+
|                           |          |                           |
|  PostgreSQL 16            |   SSH    |  Almacenamiento backups   |
|  + PostGIS                |--------->|                           |
|  + pg_cron                |  rsync   |  /backups/                |
|                           |          |    /daily/     (7 ultimos)|
|  WAL archiving            |          |    /weekly/    (4 ultimas)|
|  -> /backups/wal/         |--------->|    /monthly/   (12 ultimos|
|                           |  rsync   |    /wal/       (WAL cont.)|
+---------------------------+          +---------------------------+
```

**El usuario pidio explicitamente que los backups se envien a OTRO VPS.** Esta arquitectura cumple ese requerimiento.

#### 3.1.2 Tipos de Backup

| Tipo | Frecuencia | Herramienta | Retencion |
|------|-----------|-------------|-----------|
| Full dump | Diario 02:00 | pg_dump --format=custom | 7 dias |
| Full dump | Semanal (dom 03:00) | pg_dump --format=custom | 4 semanas |
| Full dump | Mensual (1ro 04:00) | pg_dump --format=custom | 12 meses |
| WAL archiving | Continuo | archive_command | 7 dias |
| Base backup | Semanal (dom 05:00) | pg_basebackup | 2 semanas |

#### 3.1.3 WAL Archiving para Point-in-Time Recovery

```bash
# En postgresql.conf (via docker compose command)
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /backups/wal/%f && cp %p /backups/wal/%f'
archive_timeout = 300  # Forzar archive cada 5 minutos aunque no haya actividad
```

Esto permite restaurar a CUALQUIER segundo entre backups.

### 3.2 Implementacion Tecnica

#### 3.2.1 Script de Backup Diario

```bash
#!/bin/bash
# /scripts/backup_daily.sh
# Ejecutar via cron a las 02:00

set -euo pipefail

# Variables
BACKUP_DIR="/backups/daily"
REMOTE_USER="backup"
REMOTE_HOST="vps-backup.protegrt.com"
REMOTE_DIR="/backups/daily"
DB_NAME="protegrt_db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${DATE}.dump"
LOG_FILE="/var/log/backup.log"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
TELEGRAM_ADMIN_CHAT="${TELEGRAM_ADMIN_CHAT_ID}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

alert_telegram() {
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_ADMIN_CHAT}" \
        -d "text=$1" > /dev/null 2>&1 || true
}

log "=== INICIO BACKUP DIARIO ==="

# 1. Crear backup local
log "Creando backup: ${BACKUP_FILE}"
pg_dump \
    --format=custom \
    --compress=9 \
    --verbose \
    --file="${BACKUP_FILE}" \
    "${DB_NAME}" 2>> "$LOG_FILE"

if [ $? -ne 0 ]; then
    log "ERROR: pg_dump fallo"
    alert_telegram "BACKUP FALLIDO: pg_dump error en ${DB_NAME} (${DATE})"
    exit 1
fi

BACKUP_SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
log "Backup creado: ${BACKUP_SIZE}"

# 2. Verificar integridad
log "Verificando integridad..."
pg_restore --list "${BACKUP_FILE}" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    log "ERROR: Verificacion de integridad fallo"
    alert_telegram "BACKUP CORRUPTO: Verificacion fallo en ${DB_NAME} (${DATE})"
    exit 1
fi
log "Integridad verificada OK"

# 3. Enviar a VPS remoto
log "Enviando a ${REMOTE_HOST}..."
rsync -avz --progress \
    -e "ssh -i /root/.ssh/backup_key -o StrictHostKeyChecking=yes" \
    "${BACKUP_FILE}" \
    "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"

if [ $? -ne 0 ]; then
    log "ERROR: rsync fallo"
    alert_telegram "BACKUP ERROR: rsync a ${REMOTE_HOST} fallo (${DATE})"
    exit 1
fi
log "Backup enviado a VPS remoto"

# 4. Enviar WALs acumulados
rsync -avz --progress \
    -e "ssh -i /root/.ssh/backup_key -o StrictHostKeyChecking=yes" \
    /backups/wal/ \
    "${REMOTE_USER}@${REMOTE_HOST}:/backups/wal/"

# 5. Limpiar backups locales antiguos (mantener 7 dias)
find "${BACKUP_DIR}" -name "*.dump" -mtime +7 -delete
log "Backups locales antiguos eliminados"

# 6. Limpiar WALs antiguos (mantener 7 dias)
find /backups/wal/ -name "*.gz" -mtime +7 -delete

log "=== BACKUP DIARIO COMPLETADO (${BACKUP_SIZE}) ==="
alert_telegram "Backup OK: ${DB_NAME} (${DATE}) - ${BACKUP_SIZE}"
```

#### 3.2.2 Cron Configuration

```cron
# /etc/cron.d/protegrt-backup
# Backup diario a las 02:00
0 2 * * * root /scripts/backup_daily.sh

# Backup semanal (domingo 03:00) - copia a directorio weekly
0 3 * * 0 root /scripts/backup_weekly.sh

# Backup mensual (dia 1 a las 04:00) - copia a directorio monthly
0 4 1 * * root /scripts/backup_monthly.sh

# pg_basebackup semanal (domingo 05:00)
0 5 * * 0 root /scripts/basebackup_weekly.sh

# Sincronizacion de WAL cada 15 minutos
*/15 * * * * root /scripts/sync_wal.sh

# Prueba de restauracion automatica (sabado 06:00)
0 6 * * 6 root /scripts/test_restore.sh
```

#### 3.2.3 Transferencia Segura entre VPS

```bash
# Configuracion SSH para backup
# En VPS principal: generar key pair dedicada
ssh-keygen -t ed25519 -f /root/.ssh/backup_key -N "" -C "backup@protegrt"

# En VPS backup: crear usuario restringido
useradd -m -s /bin/rbash backup
mkdir -p /home/backup/.ssh /backups/{daily,weekly,monthly,wal}
chown -R backup:backup /home/backup /backups

# Restringir el usuario backup a solo rsync
# En /home/backup/.ssh/authorized_keys:
command="rsync --server -vlogDtprze.iLsfxC . /backups/",no-port-forwarding,no-agent-forwarding,no-pty ssh-ed25519 AAAA...
```

#### 3.2.4 Verificacion de Integridad

```bash
#!/bin/bash
# /scripts/test_restore.sh
# Ejecutar semanalmente para verificar que los backups son restaurables

set -euo pipefail

LATEST_BACKUP=$(ls -t /backups/daily/*.dump | head -1)
TEST_DB="protegrt_restore_test"

log "Probando restauracion de: ${LATEST_BACKUP}"

# Crear BD temporal
createdb "${TEST_DB}"

# Restaurar
pg_restore \
    --dbname="${TEST_DB}" \
    --verbose \
    --clean \
    --if-exists \
    "${LATEST_BACKUP}" 2>> "$LOG_FILE"

# Verificar conteos basicos
POLICY_COUNT=$(psql -d "${TEST_DB}" -t -c "SELECT COUNT(*) FROM policy")
PAYMENT_COUNT=$(psql -d "${TEST_DB}" -t -c "SELECT COUNT(*) FROM payment")
CLIENT_COUNT=$(psql -d "${TEST_DB}" -t -c "SELECT COUNT(*) FROM client")

log "Restauracion OK: ${POLICY_COUNT} polizas, ${PAYMENT_COUNT} pagos, ${CLIENT_COUNT} clientes"

# Limpiar
dropdb "${TEST_DB}"

alert_telegram "Prueba de restauracion OK: ${POLICY_COUNT} polizas, ${PAYMENT_COUNT} pagos"
```

### 3.3 RPO/RTO

#### 3.3.1 Objetivos

| Metrica | Valor | Justificacion |
|---------|-------|---------------|
| **RPO** (maximo datos perdidos) | **5 minutos** | WAL archiving cada 5 min + sync cada 15 min |
| **RTO** (tiempo para restaurar) | **30 minutos** | pg_restore de dump custom + replay WAL |

#### 3.3.2 Plan de Disaster Recovery

```
Escenario 1: Corrupcion de datos (error humano, bug)
  1. Identificar el momento exacto del error en audit_log
  2. Usar PITR (Point-In-Time Recovery) para restaurar al segundo antes del error
  3. RTO: 15-30 minutos

Escenario 2: VPS principal caido (hardware failure)
  1. Provisionar nuevo VPS en EasyPanel
  2. Restaurar ultimo backup completo desde VPS backup
  3. Aplicar WALs para llegar al punto mas reciente
  4. Actualizar DNS para apuntar al nuevo VPS
  5. RTO: 30-60 minutos

Escenario 3: Ambos VPS caidos (desastre regional)
  1. Los backups mensuales tambien se copian a almacenamiento frio (S3/Backblaze)
  2. Provisionar en otra region
  3. Restaurar desde almacenamiento frio
  4. RPO: hasta 24 horas (ultimo backup diario sincronizado)
  5. RTO: 2-4 horas

Procedimiento de restauracion PITR:
  1. Parar PostgreSQL
  2. Restaurar pg_basebackup mas reciente
  3. Configurar recovery.conf con target_time
  4. Iniciar PostgreSQL en modo recovery
  5. PostgreSQL aplica WALs hasta el punto deseado
  6. Verificar datos y promover a produccion
```

---

## 4. MIGRACION DE DATOS MYSQL A POSTGRESQL

### 4.1 Estrategia

#### 4.1.1 Orden de Migracion (Respetando Foreign Keys)

```
Fase 1: Catalogos (sin dependencias)
  1. municipality
  2. department
  3. role
  4. permission
  5. role_permission
  6. coverage

Fase 2: Entidades base
  7. address (con PostGIS geom)
  8. app_user
  9. seller
  10. collector
  11. adjuster

Fase 3: Entidades de negocio principales
  12. client (FK: address)
  13. vehicle
  14. policy (FK: client, vehicle, coverage, seller, app_user)
  15. card (FK: policy, seller)

Fase 4: Transacciones
  16. payment (FK: policy, seller, collector, app_user)
  17. payment_proposal (FK: payment, policy, seller, collector, app_user)
  18. receipt (FK: policy, collector, payment)
  19. receipt_loss_schedule

Fase 5: Operaciones
  20. cancellation (FK: policy, app_user)
  21. endorsement (FK: policy, client, vehicle)
  22. renewal (FK: policy x2)
  23. collection_assignment (FK: card, policy)
  24. policy_amplia_detail (FK: policy)

Fase 6: Siniestros y servicios
  25. hospital / workshop (FK: address)
  26. tow_provider (FK: address)
  27. incident (FK: policy, address, adjuster, app_user)
  28. tow_service (FK: policy, address x2, tow_provider, app_user)
  29. medical_pass / workshop_pass (FK: incident, hospital/workshop)
  30. adjuster_shift (FK: adjuster)
  31. incident_satisfaction_survey / tow_satisfaction_survey

Fase 7: Mensajeria
  32. sent_message (FK: policy, app_user)
  33. policy_notification (FK: policy, seller)
  34. renewal_notification_log (FK: policy)

Fase 8: Promociones
  35. promotion
  36. promotion_rule (FK: promotion)
  37. promotion_application (FK: promotion, promotion_rule, policy)
  38. commission_rate (FK: coverage)

Fase 9: Tablas de sistema
  39. session / device_session (FK: app_user)
  40. execution_log
  41. visit_notice (FK: card, policy, payment)
```

#### 4.1.2 Mapeo de Tipos de Datos

| MySQL | PostgreSQL | Notas |
|-------|-----------|-------|
| INT AUTO_INCREMENT | SERIAL | Equivalente directo |
| BIGINT AUTO_INCREMENT | BIGSERIAL | Para address, client, audit_log |
| VARCHAR(N) | VARCHAR(N) | Sin cambio |
| TEXT | TEXT | Sin cambio |
| DECIMAL(M,N) | NUMERIC(M,N) | Equivalente |
| DATE | DATE | Sin cambio |
| DATETIME | TIMESTAMPTZ | Agregar zona horaria (America/Mexico_City) |
| TINYINT(1) | BOOLEAN | 0->FALSE, 1->TRUE |
| ENUM('a','b','c') | CREATE TYPE...AS ENUM | Definir tipo antes de tabla |
| INT (folio FK) | INT (policy_id FK) | Requiere tabla de mapeo folio->id |

#### 4.1.3 Transformaciones de Datos

| Campo MySQL | Transformacion | Campo PostgreSQL |
|-------------|---------------|-----------------|
| polizas.folio (PK relacional) | Mapear a policy.id (SERIAL) + conservar como policy.folio | policy.id (PK), policy.folio (UNIQUE) |
| polizas.status texto libre | Mapear a ENUM: 'Activa'->'active', 'Morosa'->'morosa', etc. | policy.status (policy_status_type) |
| pagos.status texto libre | 'PAGADO'->'paid', 'PENDIENTE'->'pending', 'ATRASADO'->'late', 'VENCIDO'->'overdue', 'CANCELADO'->'cancelled' | payment.status (payment_status_type) |
| pagos.metodo_pago texto | 'EFECTIVO'->'cash', 'TRANSFERENCIA'->'transfer', 'DEPOSITO'->'deposit' (NOTA: ver issue B8, ENUM incompleto) | payment.payment_method |
| polizas.forma_pago texto | 'Contado'->'cash', 'Contado 2 Exibiciones'->'cash_2_installments', 'Mensual 7 Mensualidades'->'monthly_7' (NOTA: ver issue B9) | policy.payment_plan |
| polizas.tipo_vehiculo texto | 'AUTOMOVIL'->'automobile', 'PICK UP'->'truck', etc. | vehicle.vehicle_type (ENUM) |
| recibos_new.status texto | 'SIN ASIGNAR'->'unassigned', 'ASIGNADO'->'assigned', etc. | receipt.status (receipt_status_type) |
| tarjetas.status texto | 'VIGENTE'->'active', 'LIQUIDADA'->'paid_off', etc. | card.status (card_status_type) |
| DATETIME sin TZ | Convertir a TIMESTAMPTZ con 'America/Mexico_City' | TIMESTAMPTZ |
| direccion campos en clientes | Normalizar a tabla address separada | client.address_id FK |

**Issues pendientes del schema que afectan migracion (del INFORME_OPTIMIZACION):**
- B8: `payment_method_type` ENUM le faltan: deposit, crucero, konfio, terminal_banorte. AGREGAR ANTES de migrar.
- B9: `payment_plan_type` ENUM incorrecto: cambiar monthly_12 por monthly_7, eliminar semester/quarterly.
- B10: `policy` falta campo `prima_total NUMERIC(12,2)`. AGREGAR ANTES de migrar.
- B11: `client` falta campo `rfc VARCHAR(20)`. AGREGAR ANTES de migrar.
- B12: `collector.receipt_limit` default deberia ser 50, no 5.

### 4.1.4 Migracion de Unificacion de Empleados

**Contexto:** Antes de la migracion grande MySQL -> PostgreSQL, el sistema MySQL actual debe unificar las tablas de vendedor, cobrador, usuarios y ajustadores en una sola tabla `empleados`. Los scripts de referencia para esta unificacion estan en `database/migrations/`:

| Script | Descripcion |
|--------|-------------|
| `unificar_empleados_001_schema.sql` | Crea tabla `empleados`, `ubicaciones_virtuales`, vista `v_asignacion_cobrador` |
| `unificar_empleados_002_data.sql` | Migra datos de `vendedor`, `cobrador`, `usuarios`, `adjusters` -> `empleados` |
| `unificar_empleados_003_cleanup.sql` | Elimina tablas antiguas (`vendedor`, `cobrador`, `usuarios`, `adjusters`) |
| `004_roles_permisos.sql` | Actualiza roles, departamentos, soporte multi-departamento |

**Estos scripts son para el sistema MySQL actual y sirven como referencia para la migracion a PostgreSQL.**

**Orden de ejecucion:**
1. Ejecutar los scripts de unificacion en MySQL (001, 002, 003, 004)
2. Verificar que la tabla `empleados` contiene todos los datos unificados
3. Proceder con la migracion grande MySQL -> PostgreSQL

**En la migracion MySQL -> PostgreSQL, la tabla unificada `empleados` ya sera la FUENTE** (porque MySQL habra sido unificado antes de la migracion grande). El mapeo es:

| MySQL (ya unificado) | PostgreSQL | Notas |
|---------------------|-----------|-------|
| `empleados` | `employee` | Tabla principal unificada de empleados |
| `ubicaciones_virtuales` | `virtual_location` | Ubicaciones para geofencing/asignacion |
| `empleado_departamentos` | `employee_department` | Relacion empleado-departamento (multi-departamento, flag `es_gerente`) |
| `empleado_permiso_override` | `employee_permission_override` | Permisos individuales concedidos/revocados por empleado |

**Esto reemplaza las migraciones separadas de seller, collector y adjuster** en la Fase 2 del orden de migracion (seccion 4.1.1). En lugar de migrar `seller`, `collector` y `adjuster` por separado, se migra la tabla unificada `empleados` directamente a `employee`.

### 4.2 Script de Migracion (Pseudocodigo)

```python
"""
Script de migracion MySQL -> PostgreSQL
Ejecutar en un entorno con acceso a ambas bases de datos.
SIEMPRE ejecutar primero en staging con datos reales.
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Dict, Tuple

# Conexiones
mysql_conn = connect_mysql("proteg_db")
pg_conn = connect_postgresql("protegrt_db")

# Zona horaria para conversion DATETIME -> TIMESTAMPTZ
TZ = "America/Mexico_City"

# =====================================================
# PASO 0: Corregir ENUMs antes de migrar
# =====================================================
def fix_enums():
    """Corregir issues B8, B9 del INFORME_OPTIMIZACION"""
    pg_conn.execute("""
        ALTER TYPE payment_method_type ADD VALUE IF NOT EXISTS 'deposit';
        ALTER TYPE payment_method_type ADD VALUE IF NOT EXISTS 'crucero';
        ALTER TYPE payment_method_type ADD VALUE IF NOT EXISTS 'konfio';
        ALTER TYPE payment_method_type ADD VALUE IF NOT EXISTS 'terminal_banorte';
    """)
    # B9: Requiere recrear el ENUM (PG no permite eliminar valores)
    # Solucion: crear nuevo tipo y migrar
    pg_conn.execute("""
        ALTER TYPE payment_plan_type RENAME TO payment_plan_type_old;
        CREATE TYPE payment_plan_type AS ENUM ('cash', 'cash_2_installments', 'monthly_7');
        ALTER TABLE policy ALTER COLUMN payment_plan TYPE payment_plan_type
            USING payment_plan::text::payment_plan_type;
        DROP TYPE payment_plan_type_old;
    """)
    # B10: Agregar prima_total
    pg_conn.execute("""
        ALTER TABLE policy ADD COLUMN IF NOT EXISTS prima_total NUMERIC(12,2);
    """)
    # B11: Agregar rfc
    pg_conn.execute("""
        ALTER TABLE client ADD COLUMN IF NOT EXISTS rfc VARCHAR(13);
    """)
    # B12: Corregir default
    pg_conn.execute("""
        ALTER TABLE collector ALTER COLUMN receipt_limit SET DEFAULT 50;
    """)

# =====================================================
# PASO 1: Mapeos de valores
# =====================================================
POLICY_STATUS_MAP = {
    "Activa": "active",
    "Pendiente": "pending",
    "Morosa": "morosa",
    "Previgencia": "pre_effective",
    "Expirada": "expired",
    "Cancelada": "cancelled",
    "SinEstado": "no_status",
}

PAYMENT_STATUS_MAP = {
    "PAGADO": "paid",
    "PENDIENTE": "pending",
    "ATRASADO": "late",
    "VENCIDO": "overdue",
    "CANCELADO": "cancelled",
}

PAYMENT_METHOD_MAP = {
    "EFECTIVO": "cash",
    "DEPOSITO": "deposit",
    "TRANSFERENCIA": "transfer",
    "CRUCERO": "crucero",
    "KONFIO": "konfio",
    "TERMINAL BANORTE": "terminal_banorte",
}

PAYMENT_PLAN_MAP = {
    "Contado": "cash",
    "Contado 2 Exibiciones": "cash_2_installments",
    "Mensual 7 Mensualidades": "monthly_7",
}

RECEIPT_STATUS_MAP = {
    "SIN ASIGNAR": "unassigned",
    "ASIGNADO": "assigned",
    "UTILIZADO": "used",
    "ENTREGADO": "delivered",
    "CANCELADO": "cancelled",
    "EXTRAVIADO": "lost",
    "CANCELADO-SIN-ENTREGAR": "cancelled_undelivered",
}

CARD_STATUS_MAP = {
    "VIGENTE": "active",
    "LIQUIDADA": "paid_off",
    "CANCELADA": "cancelled",
    "RECUPERACION": "recovery",
}

# =====================================================
# PASO 2: Migrar catalogos
# =====================================================
def migrate_coverages():
    """Migrar tabla coverages (ya existe en PG como coverage)"""
    rows = mysql_conn.query("SELECT * FROM coverages WHERE is_active = 1")
    for row in rows:
        pg_conn.execute("""
            INSERT INTO coverage (name, vehicle_type, vehicle_key, service_type,
                credit_price, initial_payment, cash_price,
                tow_services_included, is_active, cylinder_capacity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s)
        """, (row.name, row.vehicle_type, row.vehicle_key,
              'private' if row.service_type == 'PARTICULAR' else 'commercial',
              row.credit_price, row.initial_payment, row.cash_price,
              row.tow_services_available, row.cylinder_capacity))

# =====================================================
# PASO 3: Migrar usuarios
# =====================================================
def migrate_users():
    """Migrar tabla usuarios -> app_user"""
    rows = mysql_conn.query("SELECT * FROM usuarios")
    for row in rows:
        pg_conn.execute("""
            INSERT INTO app_user (username, password_hash, first_name, last_name,
                email, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (row.username, row.password, row.nombre,
              row.apellido or '', row.email,
              row.status == 'activo',
              to_timestamptz(row.created_at), to_timestamptz(row.updated_at)))
    # NOTA: Los passwords actuales NO usan bcrypt.
    # Se debe forzar reset de password en primer login del nuevo sistema.

# =====================================================
# PASO 4: Migrar clientes + direcciones
# =====================================================
def migrate_clients():
    """Migrar clientes y normalizar direcciones a tabla address"""
    rows = mysql_conn.query("SELECT * FROM clientes")
    for row in rows:
        # Crear address primero
        address_id = None
        if row.direccion_calle:
            result = pg_conn.execute("""
                INSERT INTO address (street, exterior_number, interior_number,
                    neighborhood, postal_code)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (row.direccion_calle, row.direccion_numero_ext,
                  row.direccion_numero_int, row.direccion_colonia,
                  str(row.codigo_postal) if row.codigo_postal else None))
            address_id = result.fetchone()[0]

        # Crear client
        pg_conn.execute("""
            INSERT INTO client (first_name, paternal_surname, maternal_surname,
                address_id, phone_1, phone_2, email, rfc,
                created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (row.nombre, row.apellido_paterno, row.apellido_materno,
              address_id, row.telefono_1, row.telefono_2, row.email, row.rfc,
              to_timestamptz(row.created_at), to_timestamptz(row.updated_at)))

# =====================================================
# PASO 5: Migrar empleados (tabla unificada)
# =====================================================
# NOTA: Los scripts 001-004 ya unificaron vendedores, cobradores
# y ajustadores en la tabla `empleados` de MySQL.
# Aqui solo migramos esa tabla unificada a PostgreSQL.
def migrate_employees():
    rows = mysql_conn.query("SELECT * FROM empleados WHERE activo = 1")
    for row in rows:
        pg_conn.execute("""
            INSERT INTO employee (id, username, full_name, phone, email,
                es_vendedor, es_cobrador, es_ajustador,
                codigo_vendedor, codigo_cobrador, codigo_ajustador,
                telegram_id, receipt_limit, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (row.id, row.username, row.nombre_completo, row.telefono, row.email,
              row.es_vendedor, row.es_cobrador, row.es_ajustador,
              row.codigo_vendedor, row.codigo_cobrador, row.codigo_ajustador,
              row.telegram_id, row.limite_recibos or 50,
              'active' if row.activo else 'inactive',
              to_timestamptz(row.created_at)))

    # Migrar departamentos
    dept_rows = mysql_conn.query("SELECT * FROM empleado_departamentos")
    for row in dept_rows:
        pg_conn.execute("""
            INSERT INTO employee_department (employee_id, department_id, es_gerente)
            VALUES (%s, %s, %s)
        """, (row.empleado_id, row.departamento_id, row.es_gerente))

# =====================================================
# PASO 6: Migrar polizas (tabla central)
# =====================================================
def migrate_policies():
    """
    PASO CRITICO: migrar polizas y crear tabla de mapeo folio -> policy_id.
    Todas las tablas dependientes usaran este mapeo.
    """
    rows = mysql_conn.query("SELECT * FROM polizas ORDER BY folio")

    # Mapeos auxiliares
    client_map = build_client_id_map()   # id_cliente MySQL -> client.id PG
    seller_map = build_seller_id_map()   # id_vendedor MySQL -> seller.id PG
    coverage_map = build_coverage_map()  # (cobertura, tipo_vehiculo, servicio) -> coverage.id PG

    for row in rows:
        # Crear vehiculo
        vehicle_id = create_vehicle(row)

        # Buscar coverage_id
        coverage_id = coverage_map.get(
            (row.cobertura, row.tipo_vehiculo,
             'private' if row.servicio == 'PARTICULAR' else 'commercial')
        )

        # Insertar policy
        result = pg_conn.execute("""
            INSERT INTO policy (folio, client_id, vehicle_id, coverage_id,
                seller_id, service_type, contract_folio,
                effective_date, expiration_date, status,
                payment_plan, prima_total,
                tow_services_available, contract_image_path,
                quote_external_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (row.folio,
              client_map.get(row.id_cliente),
              vehicle_id,
              coverage_id,
              seller_map.get(row.id_vendedor),
              'private' if row.servicio == 'PARTICULAR' else 'commercial',
              row.folio_contrato,
              row.vigencia, row.fin_de_vigencia,
              POLICY_STATUS_MAP.get(row.status, 'no_status'),
              PAYMENT_PLAN_MAP.get(row.forma_pago),
              row.prima_total,
              row.servicios_grua_disponibles or 0,
              row.imagen_contrato,
              row.numero_cotizacion,
              to_timestamptz(row.created_at),
              to_timestamptz(row.updated_at)))

    # Crear tabla de mapeo temporal
    pg_conn.execute("""
        CREATE TEMP TABLE folio_to_policy_id AS
            SELECT id AS policy_id, folio FROM policy;
        CREATE UNIQUE INDEX ON folio_to_policy_id(folio);
    """)

# =====================================================
# PASO 7: Migrar pagos usando mapeo folio -> policy_id
# =====================================================
def migrate_payments():
    rows = mysql_conn.query("SELECT * FROM pagos ORDER BY folio, numero_pago")
    collector_map = build_collector_map()  # nombre_clave -> collector.id

    for row in rows:
        policy_id = get_policy_id_by_folio(row.folio)
        if not policy_id:
            log_skipped("payment", row.id_pago, f"folio {row.folio} no encontrado")
            continue

        collector_id = collector_map.get(row.cobrador) if row.cobrador else None

        pg_conn.execute("""
            INSERT INTO payment (policy_id, seller_id, collector_id, user_id,
                payment_number, receipt_number, due_date, actual_date,
                amount, payment_method, office_delivery_status,
                office_delivery_date, comments, status,
                created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (policy_id, seller_map.get(row.id_vendedor),
              collector_id, row.id_usuario,
              row.numero_pago, row.numero_recibo,
              row.fecha_limite, row.fecha_real,
              row.monto,
              PAYMENT_METHOD_MAP.get(row.metodo_pago),
              'delivered' if row.entregado_en_oficina == 'ENTREGADO' else 'pending',
              row.fecha_entrega_oficina, row.comentarios,
              PAYMENT_STATUS_MAP.get(row.status, 'pending'),
              to_timestamptz(row.created_at),
              to_timestamptz(row.updated_at)))

# =====================================================
# PASO 8-15: Repetir para cada tabla dependiente
# =====================================================
# (Mismo patron: obtener policy_id via folio_to_policy_id)
# - migrate_cards()
# - migrate_collection_assignments()   (ex ubicacion_tarjeta)
# - migrate_receipts()
# - migrate_cancellations()
# - migrate_payment_proposals()         (ex pagos_temporales)
# - migrate_incidents()
# - migrate_tow_services()
# - migrate_endorsements()
# - migrate_sent_messages()
# - migrate_promotions()
# - migrate_policy_amplia_details()

# =====================================================
# PASO 16: Validaciones post-migracion
# =====================================================
def validate_migration():
    """Comparar conteos entre MySQL y PostgreSQL"""
    tables = [
        ("polizas", "policy"),
        ("clientes", "client"),
        ("pagos", "payment"),
        ("recibos_new", "receipt"),
        ("tarjetas", "card"),
        ("cancelaciones", "cancellation"),
        ("pagos_temporales", "payment_proposal"),
        ("vendedor", "seller"),
        ("cobrador", "collector"),
        ("coverages", "coverage"),
        ("promociones", "promotion"),
    ]

    errors = []
    for mysql_table, pg_table in tables:
        mysql_count = mysql_conn.query(f"SELECT COUNT(*) FROM {mysql_table}")[0][0]
        pg_count = pg_conn.query(f"SELECT COUNT(*) FROM {pg_table}")[0][0]

        if mysql_count != pg_count:
            errors.append(f"MISMATCH: {mysql_table}={mysql_count} vs {pg_table}={pg_count}")
        else:
            log(f"OK: {mysql_table} -> {pg_table}: {mysql_count} registros")

    # Verificar integridad referencial
    pg_conn.execute("""
        SELECT COUNT(*) FROM payment WHERE policy_id NOT IN (SELECT id FROM policy);
    """)  # Debe ser 0

    pg_conn.execute("""
        SELECT COUNT(*) FROM card WHERE policy_id NOT IN (SELECT id FROM policy);
    """)  # Debe ser 0

    return errors

# =====================================================
# FUNCION PRINCIPAL
# =====================================================
def main():
    """Ejecutar migracion completa en una transaccion"""
    pg_conn.begin()
    try:
        log("=== INICIO MIGRACION MySQL -> PostgreSQL ===")

        fix_enums()
        migrate_coverages()
        migrate_users()
        migrate_sellers()
        migrate_collectors()
        migrate_clients()
        migrate_policies()
        migrate_payments()
        migrate_cards()
        migrate_receipts()
        migrate_cancellations()
        migrate_payment_proposals()
        migrate_incidents()
        migrate_tow_services()
        migrate_endorsements()
        migrate_sent_messages()
        migrate_promotions()
        migrate_policy_amplia_details()
        migrate_collection_assignments()

        errors = validate_migration()
        if errors:
            log(f"ERRORES DE VALIDACION: {errors}")
            pg_conn.rollback()
            raise Exception("Migracion fallida: conteos no coinciden")

        pg_conn.commit()
        log("=== MIGRACION COMPLETADA EXITOSAMENTE ===")

    except Exception as e:
        pg_conn.rollback()
        log(f"ERROR: Migracion revertida. {e}")
        raise
```

### 4.3 Datos que NO Migrar

| Tabla/Dato | Motivo |
|------------|--------|
| Scripts test_*.py | No son datos de BD |
| promocion_mayo | Tabla legacy sin codigo activo. Los datos historicos se conservan en backup MySQL |
| Usuarios con password en texto plano | Se migran los registros pero se FUERZA reset de password |
| Sesiones activas | Las sesiones del sistema viejo no son validas en el nuevo |
| Archivos duplicados (endosos_search_updated, tow_service_dialog_fixed) | Solo existen en codigo, no en BD |

### 4.4 Pruebas de Migracion

#### 4.4.1 Plan de Pruebas

```
1. Migracion en staging (OBLIGATORIO antes de produccion)
   - Clonar BD MySQL de produccion
   - Ejecutar script de migracion completo
   - Validar conteos
   - Ejecutar suite de tests del nuevo sistema contra BD migrada

2. Comparacion de conteos
   - CADA tabla: COUNT(*) MySQL == COUNT(*) PostgreSQL
   - Polizas por status: GROUP BY status, comparar totales
   - Pagos por status: GROUP BY status, comparar totales
   - Polizas con pagos: verificar que cada poliza migrada tiene sus pagos

3. Verificacion de integridad referencial
   - 0 huerfanos en payment (policy_id que no existe en policy)
   - 0 huerfanos en card (policy_id que no existe en policy)
   - 0 huerfanos en receipt (payment_id que no existe en payment)
   - 0 huerfanos en cancellation, endorsement, renewal, etc.

4. Testing funcional post-migracion
   - Buscar poliza por folio: dato identico
   - Ver pagos de una poliza: montos y fechas identicos
   - Ver historial de tarjeta: movimientos identicos
   - Verificar StatusUpdater: ejecutar y comparar resultados con MySQL
   - Verificar dashboard: estadisticas coinciden

5. Pruebas de performance
   - Dashboard: < 2 segundos
   - Busqueda de poliza: < 500ms
   - Listado de pagos: < 1 segundo
```

#### 4.4.2 Rollback Plan

```
Si la migracion falla o produce datos incorrectos:

1. El sistema MySQL original sigue intacto (la migracion lee, no modifica)
2. DROP DATABASE protegrt_db en PostgreSQL
3. Recrear desde schema.sql
4. Investigar el error, corregir script, reintentar

No hay riesgo de perdida de datos porque:
- MySQL es READ ONLY durante migracion
- PostgreSQL se crea desde cero
- La migracion completa es una sola transaccion (COMMIT o ROLLBACK atomico)
```

---

## RESUMEN EJECUTIVO

### Acciones Inmediatas (Antes de Empezar Desarrollo)

1. **Rotar TODAS las credenciales** expuestas en git (S1-S6)
2. **Limpiar historial git** con BFG Repo Cleaner
3. **Configurar VPS de backup** con acceso SSH restringido
4. **Crear repositorio nuevo** (privado) para el sistema nuevo
5. **Definir variables de entorno** en EasyPanel para staging

### Seguridad: Resumen de Contramedidas

| Vulnerabilidad Actual | Contramedida |
|----------------------|-------------|
| S1-S5: Credenciales en codigo/git | Variables de entorno exclusivamente |
| S6: JWT SECRET_KEY predecible | RS256 con claves RSA asimetricas (privada en servidor, publica distribuible) |
| S9: Token sin expiracion | Access 15min + Refresh 7d con rotacion |
| S10: Sesion infinita | Limites estrictos + blacklist en Redis |
| S11-S14: SQL injection | SQLAlchemy ORM + linter CI/CD |
| S15: SSL deshabilitado | TLS 1.3 obligatorio en todo |
| S16: Acceso sin auth | Middleware en CADA endpoint |

### Backup: Garantias

| Metrica | Garantia |
|---------|---------|
| RPO | 5 minutos (WAL archiving) |
| RTO | 30 minutos (pg_restore + WAL replay) |
| Backups remotos | VPS separado (requerimiento explicito del usuario) |
| Verificacion | Prueba de restauracion automatica semanal |

### Migracion: Riesgos Controlados

| Riesgo | Mitigacion |
|--------|-----------|
| Perdida de datos | MySQL READ ONLY + transaccion atomica PG |
| Folio -> ID | Tabla temporal de mapeo + verificacion post-migracion |
| ENUMs incompletos (B8, B9) | Corregir ANTES de migrar datos |
| Campos faltantes (B10, B11) | ALTER TABLE antes de migrar |
| Datos corruptos | Validacion de conteos + integridad referencial |

---

**Fin del documento.**
