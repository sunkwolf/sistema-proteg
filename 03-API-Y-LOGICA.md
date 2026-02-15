# 03 - API REST Completa y Logica de Negocio

**Proyecto:** Nuevo CRM Protegrt
**Version:** 1.0
**Fecha:** 2026-02-14
**Autor:** Agente API Designer

> **NOTA:** Las decisiones tecnicas canonicas estan en `CLAUDE.md` seccion "Decisiones Canonicas v1".
> En caso de contradiccion entre este documento y CLAUDE.md, CLAUDE.md prevalece.

---

## INDICE

1. [Convenciones Generales](#1-convenciones-generales)
2. [Autenticacion y Seguridad (Auth)](#2-autenticacion-y-seguridad)
3. [Clientes](#3-clientes)
4. [Vehiculos](#4-vehiculos)
5. [Coberturas](#5-coberturas)
6. [Polizas](#6-polizas)
7. [Pagos](#7-pagos)
8. [Panel de Autorizacion (Pagos y Polizas)](#8-panel-de-autorizacion-pagos-y-polizas)
9. [Recibos](#9-recibos)
10. [Tarjetas y Cobranza](#10-tarjetas-y-cobranza)
11. [Empleados (Unificado)](#11-empleados-unificado)
12. [Cancelaciones](#12-cancelaciones)
13. [Renovaciones](#13-renovaciones)
14. [Siniestros](#14-siniestros)
15. [Gruas](#15-gruas)
16. [Endosos](#16-endosos)
17. [Promociones](#17-promociones)
18. [Cotizaciones (Integracion Externa)](#18-cotizaciones)
19. [Notificaciones](#19-notificaciones)
20. [Reportes](#20-reportes)
21. [Dashboard](#21-dashboard)
22. [Administracion](#22-administracion)
23. [Flujo Pendiente de Autorizacion (Completo)](#23-flujo-pendiente-de-autorizacion)
24. [Sistema de Promociones (Completo)](#24-sistema-de-promociones)
25. [Sistema de Notificaciones (Completo)](#25-sistema-de-notificaciones)
26. [Logica de Negocio Mejorada](#26-logica-de-negocio-mejorada)

---

## 1. CONVENCIONES GENERALES

### 1.1 Base URL

```
Produccion:  https://api.protegrt.com/api/v1
Staging:     https://api-staging.protegrt.com/api/v1
```

### 1.2 Formato de Request/Response

- Content-Type: `application/json`
- Encoding: UTF-8
- Fechas: ISO 8601 (`2026-02-14`, `2026-02-14T10:30:00Z`)
- Montos: string con 2 decimales (`"1500.00"`) para evitar precision de punto flotante
- IDs: integer

### 1.3 Paginacion

Toda lista paginada usa el formato:

```json
// Request: GET /api/v1/resource?page=1&page_size=25&sort_by=created_at&sort_order=desc
// Response:
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total_items": 342,
    "total_pages": 14
  }
}
```

### 1.4 Errores

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "El campo folio_contrato ya existe",
    "details": [
      {"field": "folio_contrato", "message": "Valor duplicado: 12345"}
    ]
  }
}
```

Codigos HTTP:
- `200` OK
- `201` Creado
- `204` Sin contenido (DELETE exitoso)
- `400` Error de validacion
- `401` No autenticado
- `403` Sin permisos
- `404` No encontrado
- `409` Conflicto (duplicado)
- `422` Entidad no procesable (logica de negocio)
- `429` Rate limit
- `500` Error interno

### 1.5 Autenticacion en headers

```
Authorization: Bearer <access_token>
X-Device-Id: <device_uuid>  (solo apps moviles)
```

### 1.6 Roles del sistema

| Rol | Codigo | Descripcion |
|-----|--------|-------------|
| Administrador | `admin` | Acceso total al sistema |
| Gerente | `gerente` | Gestion de su(s) departamento(s), aprobar solicitudes |
| Auxiliar | `auxiliar` | Operaciones limitadas de departamento |
| Cobrador | `collector` | App movil: registrar cobros, ver ruta |
| Vendedor | `seller` | App movil: crear polizas, cotizar |
| Ajustador | `adjuster` | App movil: atender siniestros |
| Solo Lectura | `viewer` | Consulta sin modificar |

#### 1.6.1 Roles de sistema vs Roles de negocio

Los roles de la tabla anterior son **roles de sistema** (para login y permisos). Determinan que puede hacer el usuario en la aplicacion.

Los **roles de negocio** (vendedor, cobrador, ajustador) son **FLAGS en el registro del empleado**, no roles de sistema separados:
- `es_vendedor`: el empleado vende polizas
- `es_cobrador`: el empleado cobra pagos en campo
- `es_ajustador`: el empleado atiende siniestros

**Un empleado puede tener MULTIPLES roles de negocio simultaneamente.** Por ejemplo, una persona puede ser vendedor + cobrador + ajustador al mismo tiempo.

**Gerente es por departamento**, no un rol global. Se define en `empleado_departamentos.es_gerente`. Un empleado puede ser gerente de un departamento y no de otro.

**Overrides de permisos individuales:** La tabla `empleado_permiso_override` permite conceder o revocar permisos individuales mas alla del default del rol. Esto permite ajuste fino sin crear roles adicionales.

---

## 2. AUTENTICACION Y SEGURIDAD

### 2.1 Endpoints

| Metodo | Ruta | Descripcion | Auth |
|--------|------|-------------|------|
| POST | `/auth/login` | Iniciar sesion | No |
| POST | `/auth/refresh` | Renovar access token | Refresh token |
| POST | `/auth/logout` | Cerrar sesion | Si |
| POST | `/auth/logout-all` | Cerrar todas las sesiones | Si |
| GET | `/auth/me` | Perfil del usuario autenticado | Si |
| PUT | `/auth/me/password` | Cambiar contrasena propia | Si |
| POST | `/auth/mobile/login` | Login desde app movil | No |
| POST | `/auth/mobile/refresh` | Refresh desde app movil | Refresh token |

### 2.2 POST /auth/login

**Request:**
```json
{
  "username": "juan.perez",
  "password": "mi_contrasena_segura"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": 4,
    "username": "oscar",
    "nombre_completo": "Oscar Lopez",
    "roles_negocio": {
      "es_vendedor": true,
      "es_cobrador": true,
      "es_ajustador": true
    },
    "rol_sistema": {"id": 1, "nombre": "Administrador"},
    "departamentos": [
      {"id": 1, "nombre": "Administracion", "es_gerente": false},
      {"id": 2, "nombre": "Ventas", "es_gerente": false}
    ],
    "permissions": ["polizas_read", "polizas_write", "pagos_read", ...]
  }
}
```

**Reglas:**
- NO "recordar sesion" / remember me. Las PCs se comparten entre multiples personas
- Access token: JWT RS256, expira en 15 minutos
- Refresh token: UUID opaco, expira en 7 dias (web) / 30 dias (movil), almacenado en httpOnly cookie + Redis
- Claves RSA: par publico/privado en variables de entorno (JWT_PRIVATE_KEY, JWT_PUBLIC_KEY)
- Registra sesion en tabla `session` con IP y user-agent
- Bloqueo despues de 5 intentos fallidos en 15 minutos (desbloqueo automatico)

### 2.3 POST /auth/mobile/login

**Request:**
```json
{
  "username": "edgar_cobrador",
  "password": "contrasena",
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "device_type": "android",
  "app_type": "collector_app",
  "app_version": "1.0.0",
  "push_token": "fcm_token_aqui"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900,
  "user": {
    "id": 94,
    "username": "edgar_cobrador",
    "roles_negocio": {"es_vendedor": false, "es_cobrador": true, "es_ajustador": false},
    "nombre_clave": "EDGAR",
    "nombre_completo": "EDGAR EDUARDO GONZALEZ PEREZ"
  }
}
```

**Reglas:**
- Registra en `device_session`
- Un usuario puede tener multiples dispositivos activos
- Push token se actualiza si cambia

### 2.4 Verificacion de permisos

El sistema usa un middleware que verifica:

```python
# Jerarquia
1. Si no hay token -> 401
2. Si token expirado -> 401 (usar refresh)
3. Si rol == "admin" -> permitir TODO
4. Si es_gerente en departamento del recurso -> acceso al modulo de su departamento
5. Verificar permiso base del rol en rol_permiso
6. Verificar override individual en empleado_permiso_override (concedido/revocado)
```

**Permisos por modulo:**

| Modulo | Lectura | Escritura |
|--------|---------|-----------|
| Dashboard | `dashboard_access` | - |
| Clientes | `clientes_read` | `clientes_write` |
| Polizas | `polizas_read` | `polizas_write` |
| Pagos | `pagos_read` | `cobranza_write` |
| Cobranza | `cobranza_access` | `cobranza_access` |
| Siniestros | `siniestros_read` | `siniestros_write` |
| Gruas | `siniestros_read` | `siniestros_write` |
| Recibos | `recibos_read` | `recibos_write` |
| Promociones | `promociones_read` | `promociones_write` |
| Reportes | `reportes_read` | - |
| Usuarios | `usuarios_admin` | `usuarios_admin` |
| Admin Panel | `admin_panel_access` | `admin_panel_access` |

---

## 3. CLIENTES

### 3.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/clients` | Listar clientes (paginado, filtros) | `clientes_read` |
| GET | `/clients/:id` | Detalle de un cliente | `clientes_read` |
| POST | `/clients` | Crear cliente | `clientes_write` |
| PUT | `/clients/:id` | Actualizar cliente | `clientes_write` |
| DELETE | `/clients/:id` | Soft-delete cliente | `admin` |
| GET | `/clients/:id/policies` | Polizas del cliente | `clientes_read` |
| GET | `/clients/:id/payments` | Historial de pagos del cliente | `clientes_read` |
| GET | `/clients/search` | Busqueda por similitud (pg_trgm) | `clientes_read` |

### 3.2 GET /clients

> **RESTRICCION DE SEGURIDAD:** NO se permite exportar lista de clientes a CSV/Excel por seguridad. Solo consulta en pantalla.

**Query params:**
```
?page=1&page_size=25
&search=Juan Perez              # busqueda pg_trgm en nombre completo
&phone=3311234567               # busqueda exacta por telefono
&municipality_id=5              # filtro por municipio
&has_active_policy=true         # solo clientes con poliza activa
&sort_by=paternal_surname       # created_at, first_name, paternal_surname
&sort_order=asc
```

### 3.3 POST /clients

**Request:**
```json
{
  "first_name": "Juan",
  "paternal_surname": "Perez",
  "maternal_surname": "Lopez",
  "whatsapp": "3311234567",
  "phone_additional": null,
  "email": "juan@email.com",
  "rfc": "PELJ900101ABC",
  "address": {
    "street": "Avenida Vallarta",
    "exterior_number": "1234",
    "interior_number": null,
    "neighborhood": "Americana",
    "municipality_id": 5,
    "postal_code": "44160",
    "latitude": 20.6736,
    "longitude": -103.3650
  }
}
```

**Validaciones:**
1. `first_name`: obligatorio, max 50 chars
2. `paternal_surname`: obligatorio, max 50 chars
3. `whatsapp`: obligatorio, debe ser 10 digitos (telefono mexicano). Numero de WhatsApp (se verifica via Evolution API)
4. `phone_additional`: opcional, 10 digitos si se proporciona
5. `email`: formato email valido si se proporciona
6. `rfc`: formato RFC mexicano si se proporciona (13 chars persona fisica, 12 chars persona moral)
7. `address.latitude` + `address.longitude`: si se proporcionan ambos, se crea punto PostGIS automaticamente
8. Strings vacios se convierten a `null` (mantiene comportamiento actual)
9. `postal_code`, `municipality_id`: se castean a tipo correcto, null si fallan

> **NOTA:** Al crear un nuevo cliente, se envia mensaje de verificacion por WhatsApp al numero proporcionado.

**Response 201:**
```json
{
  "id": 1,
  "first_name": "Juan",
  "paternal_surname": "Perez",
  "maternal_surname": "Lopez",
  "whatsapp": "3311234567",
  "phone_additional": null,
  "email": "juan@email.com",
  "rfc": "PELJ900101ABC",
  "address": {
    "id": 1,
    "street": "Avenida Vallarta",
    "exterior_number": "1234",
    "neighborhood": "Americana",
    "municipality": {"id": 5, "name": "Guadalajara"},
    "postal_code": "44160"
  },
  "created_at": "2026-02-14T10:30:00Z"
}
```

---

## 4. VEHICULOS

### 4.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/vehicles` | Listar vehiculos | `polizas_read` |
| GET | `/vehicles/:id` | Detalle de vehiculo | `polizas_read` |
| POST | `/vehicles` | Crear vehiculo | `polizas_write` |
| PUT | `/vehicles/:id` | Actualizar vehiculo | `polizas_write` |
| GET | `/vehicles/by-serial/:serial` | Buscar por numero de serie | `polizas_read` |
| GET | `/vehicles/by-plates/:plates` | Buscar por placas | `polizas_read` |

### 4.2 POST /vehicles

**Request:**
```json
{
  "brand": "NISSAN",
  "model_type": "VERSA",
  "model_year": "2024",
  "color": "BLANCO",
  "vehicle_key": 101,
  "vehicle_type": "automobile",
  "serial_number": "3N1CN7AD3PK123456",
  "plates": "JAL-1234",
  "cylinder_capacity": null,
  "seats": 5
}
```

**Validaciones:**
1. `brand`: obligatorio
2. `serial_number`: unico si se proporciona
3. `vehicle_key`: debe ser uno de 101, 103, 105, 107, 108, 109
4. `vehicle_type`: debe corresponder al vehicle_key (101=automobile, 103=truck, 105=suv, 107=motorcycle, 108=mototaxi, 109 no tiene enum aun)
5. `cylinder_capacity`: solo requerido si vehicle_type = motorcycle o mototaxi

**Claves vehiculares internas:**

| vehicle_key | vehicle_type | Nombre negocio |
|-------------|-------------|----------------|
| 101 | automobile | AUTOMOVIL |
| 103 | truck | PICK UP |
| 105 | suv | CAMIONETA |
| 107 | motorcycle | MOTOCICLETA |
| 108 | mototaxi | MOTO TAXI |
| 109 | (pendiente) | CAMION |

---

## 5. COBERTURAS

### 5.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/coverages` | Listar coberturas | `polizas_read` |
| GET | `/coverages/:id` | Detalle de cobertura | `polizas_read` |
| POST | `/coverages` | Crear cobertura | `admin` |
| PUT | `/coverages/:id` | Actualizar cobertura | `admin` |
| GET | `/coverages/search` | Buscar por criterios | `polizas_read` |
| GET | `/coverages/:id/payment-schemes` | Esquemas de pago | `polizas_read` |

### 5.2 GET /coverages/search

**Query params:**
```
?vehicle_type=AUTOMOVIL
&name=PLATINO
&service_type=private
&cylinder_capacity=901 A 1800 CC     # solo para motos
```

**Logica de busqueda (preservada del sistema actual):**
- Para MOTOCICLETA con cilindraje: filtra por `cylinder_capacity = valor`
- Para MOTOCICLETA sin cilindraje: filtra por `cylinder_capacity IS NULL`
- Para otros vehiculos: filtra por `cylinder_capacity IS NULL`
- Solo busca coberturas activas (`is_active = true`)

### 5.3 GET /coverages/:id/payment-schemes

**Response:**
```json
{
  "coverage": {
    "id": 1,
    "name": "PLATINO",
    "vehicle_type": "AUTOMOVIL",
    "service_type": "private"
  },
  "schemes": {
    "cash": {
      "total": "3500.00",
      "payments": [{"number": 1, "amount": "3500.00"}]
    },
    "cash_2_installments": {
      "total": "3500.00",
      "first_payment_editable": true,
      "payments": [
        {"number": 1, "amount": "1750.00"},
        {"number": 2, "amount": "1750.00"}
      ]
    },
    "monthly_7": {
      "total": "4200.00",
      "payments": [
        {"number": 1, "amount": "1200.00", "label": "Enganche"},
        {"number": 2, "amount": "500.00"},
        {"number": 3, "amount": "500.00"},
        {"number": 4, "amount": "500.00"},
        {"number": 5, "amount": "500.00"},
        {"number": 6, "amount": "500.00"},
        {"number": 7, "amount": "500.00"}
      ]
    }
  }
}
```

**Logica de calculo (preservada):**

1. **AMPLIA / AMPLIA SELECT:** Retorna 0.00 para todo (precio depende del vehiculo individual, se obtiene de cotizacion externa).

2. **Contado:**
   - `primer_pago = cash_price`
   - `segundo_pago = 0`
   - Primer pago NO editable

3. **Contado 2 Exhibiciones:**
   - `primer_pago = cash_price / 2`
   - `segundo_pago = cash_price / 2`
   - Primer pago editable (el usuario puede ajustar la distribucion)

4. **Mensual 7 Mensualidades:**
   - `enganche = initial_payment`
   - `mensualidad = round((credit_price - initial_payment) / 6, 2)`
   - Total: 1 enganche + 6 mensualidades = 7 pagos

---

## 6. POLIZAS

### 6.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/policies` | Listar polizas (paginado) | `polizas_read` |
| GET | `/policies/:id` | Detalle completo de poliza | `polizas_read` |
| GET | `/policies/by-folio/:folio` | Buscar por folio de negocio | `polizas_read` |
| POST | `/policies` | Crear poliza | `polizas_write` |
| PUT | `/policies/:id` | Actualizar poliza | `polizas_write` |
| PUT | `/policies/:id/seller` | Cambiar vendedor | `polizas_write` |
| GET | `/policies/:id/payments` | Pagos de la poliza | `polizas_read` |
| GET | `/policies/:id/payment-history` | Historial visual de pagos | `polizas_read` |
| POST | `/policies/:id/restructure` | Reestructurar contado a cuotas | `admin` |
| GET | `/policies/:id/amplia-details` | Detalles AMPLIA/SELECT | `polizas_read` |
| GET | `/policies/:id/eligibility` | Elegibilidad AMPLIA SELECT | `polizas_read` |

### 6.2 GET /policies

**Query params:**
```
?page=1&page_size=25
&search=PEREZ                      # busqueda en nombre cliente o folio
&folio=18500                       # filtro exacto por folio
&status=active                     # active, pending, morosa, pre_effective, expired, cancelled
&coverage_name=PLATINO             # nombre de cobertura
&seller_id=3                       # vendedor
&client_id=100                     # cliente
&effective_date_from=2026-01-01    # rango de vigencia
&effective_date_to=2026-12-31
&sort_by=folio                     # folio, effective_date, created_at, status
&sort_order=desc
```

### 6.3 POST /policies

**Request:**
```json
{
  "client_id": 100,
  "vehicle_id": 50,
  "coverage_id": 3,
  "seller_id": 5,
  "service_type": "private",
  "contract_folio": 12345,
  "effective_date": "2026-03-01",
  "expiration_date": "2027-03-01",
  "payment_plan": "monthly_7",
  "prima_total": "4200.00",
  "tow_services_available": 2,
  "contract_image_path": "/contracts/2026/12345.jpg",
  "quote_external_id": "AUT-DC06BCB1",
  "comments": null,
  "custom_payments": null,
  "promotion_id": null
}
```

**Validaciones:**
1. `client_id`: debe existir y no estar eliminado
2. `vehicle_id`: debe existir
3. `coverage_id`: debe existir y estar activa
4. `contract_folio`: debe ser unico (no debe existir otro folio con ese contract_folio)
5. `effective_date` < `expiration_date`
6. `payment_plan`: debe ser uno de `cash`, `cash_2_installments`, `monthly_7`
7. Si cobertura es AMPLIA SELECT:
   - Solo permitida con vehicle_key 101, 103, 105
   - Requiere historial de renovacion (poliza anterior del mismo cliente)
8. `prima_total`: debe ser > 0 (excepto AMPLIA con cotizacion externa)
9. Folio de negocio: se genera automaticamente como `MAX(folio) + 1`

**Acciones automaticas al crear:**
1. Generar folio de negocio
2. Crear pagos automaticamente segun `payment_plan` y cobertura
3. Crear tarjeta (card) con ubicacion "OFICINA"
4. Si hay `promotion_id`: aplicar promocion a los pagos
5. Si hay `quote_external_id`: aprobar cotizacion via API externa
6. Status inicial: "pre_effective" si effective_date > hoy, "pending" si no

**Response 201:**
```json
{
  "id": 500,
  "folio": 18750,
  "client": {"id": 100, "full_name": "Juan Perez Lopez"},
  "vehicle": {"id": 50, "brand": "NISSAN", "model_type": "VERSA", "model_year": "2024"},
  "coverage": {"id": 3, "name": "PLATINO", "vehicle_type": "AUTOMOVIL"},
  "seller": {"id": 5, "code_name": "V01", "full_name": "Pedro Vendedor"},
  "service_type": "private",
  "contract_folio": 12345,
  "effective_date": "2026-03-01",
  "expiration_date": "2027-03-01",
  "status": "pre_effective",
  "payment_plan": "monthly_7",
  "prima_total": "4200.00",
  "tow_services_available": 2,
  "payments_summary": {
    "total_payments": 7,
    "first_payment_amount": "1200.00",
    "monthly_amount": "500.00"
  },
  "created_at": "2026-02-14T10:30:00Z"
}
```

### 6.4 PUT /policies/:id/seller

**Request:**
```json
{
  "seller_id": 8
}
```

**Acciones automaticas (preservadas del sistema actual):**
1. Actualizar `seller_id` en la poliza
2. Actualizar `seller_id` en TODOS los pagos del folio (cascada)
3. Todo en una sola transaccion

### 6.5 POST /policies/:id/restructure

Reestructurar de "Contado 2 Exhibiciones" a "Mensual 7 Mensualidades".

**Request:**
```json
{
  "reason": "Cliente no puede completar segunda exhibicion"
}
```

**Logica (preservada):**
1. Verificar que la poliza tiene payment_plan = `cash_2_installments`
2. Obtener credit_price de la cobertura
3. Calcular total pagado (pagos con status = `paid`)
4. Saldo restante = credit_price - total_pagado
5. Dividir saldo en 6 pagos mensuales: saldo / 6
6. Renumerar pagos existentes y crear los nuevos
7. Actualizar payment_plan a `monthly_7`

### 6.6 Maquina de estados de poliza

```
pre_effective -> pending -> active -> morosa -> expired
                                  \-> cancelled
```

**Reglas de transicion (por prioridad descendente):**

| Prioridad | Status | Condicion |
|-----------|--------|-----------|
| 1 (max) | `cancelled` | EXISTE algun pago con status `cancelled` |
| 2 | `morosa` | EXISTE algun pago con status `late` o `overdue` |
| 3 | `pre_effective` | fecha_actual < effective_date AND (pago 1 esta paid OR pago 1 no esta vencido) |
| 4 | `pending` | pago 1 esta `pending`; O pago fragmentado (pago 1 paid con monto reducido y pago 2 no vencido) |
| 5 | `active` | fecha_actual BETWEEN effective_date AND expiration_date AND todos los pagos vencidos estan paid |
| 6 | `expired` | fecha_actual > expiration_date |

---

## 7. PAGOS

> **RESTRICCION CRITICA:** Solo el departamento de Cobranza puede editar pagos. Los demas departamentos tienen acceso de solo lectura.

### 7.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/payments` | Listar pagos (paginado) | `pagos_read` |
| GET | `/payments/:id` | Detalle de un pago | `pagos_read` |
| POST | `/payments` | Crear pago manual | `cobranza_write` |
| PUT | `/payments/:id` | Editar pago (revision completa) | `cobranza_write` |
| POST | `/payments/:id/partial` | Registrar abono parcial | `cobranza_write` |
| POST | `/payments/:id/revert` | Revertir pago | `admin` |
| POST | `/payments/:id/mark-problem` | Marcar problema de pago | `cobranza_write` |
| GET | `/payments/by-policy/:policy_id` | Pagos de una poliza | `pagos_read` |

### 7.2 Metodos de pago

```
cash             = EFECTIVO
deposit          = DEPOSITO
transfer         = TRANSFERENCIA
crucero          = CRUCERO (cobro en campo)
konfio           = KONFIO (fintech)
terminal_banorte = TERMINAL BANORTE
```

> **NOTA CRITICA:** El schema PostgreSQL actual tiene un ENUM `payment_method_type` con valores `cash, transfer, card, check` que NO corresponden a los metodos reales. Se debe corregir a: `cash, deposit, transfer, crucero, konfio, terminal_banorte`.

### 7.3 PUT /payments/:id (Revision completa)

**Request:**
```json
{
  "receipt_number": "A0023",
  "actual_date": "2026-02-10",
  "amount": "500.00",
  "payment_method": "cash",
  "collector_id": 3,
  "office_delivery_status": "pending",
  "office_delivery_date": null,
  "status": "paid",
  "comments": "Pago recibido en domicilio"
}
```

**Validaciones (preservadas del sistema actual + mejoras):**

1. Si se proporciona `receipt_number`: debe estar verificado previamente (ver endpoint de recibos)
2. `office_delivery_status`: solo `pending` o `delivered`
3. Si `actual_date` tiene valor: `status` DEBE ser `paid`
4. `actual_date`: no mayor a 8 meses atras ni 1 mes adelante de hoy
5. Si `office_delivery_status = delivered`: `office_delivery_date` es obligatoria
6. Si `office_delivery_date` tiene valor: `office_delivery_status` debe ser `delivered`
7. Diferencia entre `office_delivery_date` y `actual_date`: maximo 30 dias

**Acciones post-edicion (preservadas):**
1. **Sincronizar recibo**: actualizar status en tabla `receipt`
2. **Actualizar status de pagos y poliza** via StatusUpdater
3. **Verificar liquidacion automatica**: si TODOS los pagos estan `paid`:
   - Mover tarjeta a ubicacion "ARCHIVO"
   - Cambiar status de tarjeta a `paid_off`
   - Registrar movimiento historico
4. **Notificar cliente por WhatsApp**: SOLO si:
   - `actual_date` tiene valor
   - `status` es `paid`
   - El recibo tenia status `assigned` ANTES de la edicion

### 7.4 POST /payments/:id/partial (Abono parcial)

**Request:**
```json
{
  "partial_amount": "300.00",
  "receipt_number": "A0024",
  "payment_method": "cash",
  "collector_id": 3
}
```

**Logica (preservada):**
1. Validar que `partial_amount < amount_original` (debe quedar saldo)
2. Validar que `partial_amount >= 0.01`
3. Actualizar pago original: amount = partial_amount, status = `paid`, actual_date = hoy
4. Crear NUEVO pago con: amount = (amount_original - partial_amount), status = `pending`, misma due_date
5. Si es pago #1: renumerar pagos subsecuentes (+1 a cada payment_number)

### 7.5 POST /payments/:id/revert

**Request:**
```json
{
  "reason": "Recibo cancelado por error"
}
```

**Acciones:**
- receipt_number = null
- actual_date = null
- collector_id = null
- office_delivery_status = null
- office_delivery_date = null
- status = `pending`
- Registra comentario: "Pago revertido por {username}, motivo: {reason}, fecha: {fecha}"
- Recalcula status de poliza via StatusUpdater

### 7.6 Maquina de estados de pago

```
pending -> late -> overdue -> paid
                           \-> cancelled
```

**Reglas de transicion automatica (job diario 00:00):**

| Status | Condicion |
|--------|-----------|
| `pending` | due_date >= hoy |
| `late` | due_date < hoy AND diferencia <= 5 dias |
| `overdue` | due_date < hoy AND diferencia > 5 dias |
| `paid` | Marcado manualmente al registrar cobro |
| `cancelled` | Solo por cancelacion de poliza |

> Solo se actualizan pagos que NO esten en `paid` ni `cancelled`.

### 7.7 Contado a Cuotas (Plan de pagos sobre saldo)

Cuando un cliente negocia pagar su deuda restante en cuotas, se utiliza este flujo. Esta funcionalidad esta integrada directamente en el modulo de Pagos (no es una vista separada).

**Endpoint:** POST `/payments/installment-plan`

**Permisos:** `cobranza_write`

**Request:**
```json
{
  "policy_id": 200,
  "remaining_amount": "2500.00",
  "num_installments": 5,
  "start_date": "2026-03-01"
}
```

**Logica:**
1. Validar que la poliza existe y tiene saldo pendiente
2. Validar que `remaining_amount` coincide con el saldo real pendiente de la poliza
3. Calcular monto por cuota: `remaining_amount / num_installments`
4. Crear nuevos registros de pago dividiendo la deuda restante
5. Asignar fechas de vencimiento mensuales a partir de `start_date`
6. Recalcular status de poliza via StatusUpdater

**Response 201:**
```json
{
  "policy_id": 200,
  "installment_plan": {
    "total_amount": "2500.00",
    "num_installments": 5,
    "amount_per_installment": "500.00",
    "payments_created": [
      {"payment_number": 4, "amount": "500.00", "due_date": "2026-03-01"},
      {"payment_number": 5, "amount": "500.00", "due_date": "2026-04-01"},
      {"payment_number": 6, "amount": "500.00", "due_date": "2026-05-01"},
      {"payment_number": 7, "amount": "500.00", "due_date": "2026-06-01"},
      {"payment_number": 8, "amount": "500.00", "due_date": "2026-07-01"}
    ]
  }
}
```

---

## 8. PANEL DE AUTORIZACION (Pagos y Polizas)

Este modulo unifica dos flujos de autorizacion:
- **a) Propuestas de pago:** propuestas de cobro enviadas por cobradores desde el campo
- **b) Autorizacion de polizas:** polizas pendientes de aprobacion

### 8.1 Endpoints de Propuestas de Pago

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/authorization/payments` | Listar propuestas | `pagos_read` |
| GET | `/authorization/payments/:id` | Detalle de propuesta | `pagos_read` |
| POST | `/authorization/payments` | Crear propuesta (cobrador en campo) | `collector` |
| PUT | `/authorization/payments/:id` | Editar propuesta (antes de aprobar) | `cobranza_write` |
| POST | `/authorization/payments/:id/approve` | Aprobar propuesta | `gerente` |
| POST | `/authorization/payments/:id/reject` | Rechazar propuesta | `gerente` |
| POST | `/authorization/payments/:id/apply` | Aplicar al pago original | `gerente` |
| POST | `/authorization/payments/:id/cancel` | Cancelar propuesta | `collector` (creador) |
| GET | `/authorization/payments/pending` | Propuestas pendientes de revision | `gerente` |
| GET | `/authorization/payments/mine` | Mis propuestas (cobrador) | `collector` |
| GET | `/authorization/payments/report` | Reporte Excel del dia | `gerente` |

### 8.2 Endpoints de Autorizacion de Polizas

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/authorization/policies/pending` | Polizas pendientes de autorizacion | `gerente` |
| POST | `/authorization/policies/:id/approve` | Aprobar poliza | `gerente` |
| POST | `/authorization/policies/:id/reject` | Rechazar poliza | `gerente` |

### 8.3 POST /authorization/payments

**Request (desde app movil de cobrador):**
```json
{
  "original_payment_id": 500,
  "policy_id": 200,
  "receipt_number": "A0030",
  "actual_date": "2026-02-14",
  "amount": "500.00",
  "payment_method": "cash",
  "comments": "Cobrado en domicilio del cliente",
  "geo_latitude": 20.6736,
  "geo_longitude": -103.3650,
  "evidence_photo_url": "/uploads/receipts/2026/02/14/photo_abc123.jpg"
}
```

**Validaciones:**
1. Verificar que NO exista otra propuesta activa para el mismo `original_payment_id`
2. Verificar que el pago original NO este en status `paid`
3. `amount` > 0
4. `receipt_number`: si se proporciona, debe ser valido y asignado al cobrador
5. El cobrador autenticado debe tener la tarjeta asignada para esta poliza

**Response 201:**
```json
{
  "id": 50,
  "original_payment_id": 500,
  "policy_folio": 18500,
  "status": "pending",
  "requires_manager": false,
  "submitted_by": {"id": 5, "username": "edgar_cobrador"},
  "submitted_at": "2026-02-14T15:30:00Z"
}
```

**Regla de escalamiento automatico:**
- Si `amount >= 5000`: `requires_manager = true` (requiere aprobacion de un gerente de departamento)

### 8.4 POST /authorization/payments/:id/approve + apply

**Flujo de aprobacion -> aplicacion:**

1. **Aprobar:** cambia status a `approved`, registra `reviewed_by` y `reviewed_at`
2. **Aplicar:** ejecuta UPDATE en el pago original con los datos de la propuesta, cambia status a `applied`
3. Post-aplicacion: mismas acciones que editar un pago normal (sincronizar recibo, StatusUpdater, verificar liquidacion, notificar WhatsApp)

### 8.5 Estados de propuesta

```
pending -> under_review -> approved -> applied
                        \-> rejected
pending -> cancelled (por el cobrador)
```

---

## 9. RECIBOS

### 9.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/receipts` | Listar recibos (paginado) | `recibos_read` |
| GET | `/receipts/:id` | Detalle de recibo | `recibos_read` |
| POST | `/receipts/batch` | Registrar lote de recibos | `recibos_write` |
| POST | `/receipts/assign` | Asignar recibos a cobrador | `recibos_write` |
| POST | `/receipts/verify` | Verificar recibo | `pagos_write` |
| POST | `/receipts/:id/cancel` | Cancelar recibo | `recibos_write` |
| POST | `/receipts/:id/mark-lost` | Marcar como extraviado | `recibos_write` |
| GET | `/receipts/by-collector/:collector_id` | Recibos de un cobrador | `recibos_read` |
| GET | `/receipts/by-number/:number` | Buscar por numero | `recibos_read` |

### 9.2 POST /receipts/batch

**Request:**
```json
{
  "prefix": "A",
  "start": 1,
  "end": 100
}
```

Genera recibos: A0001, A0002, ..., A0100. Status inicial: `unassigned`. Salta duplicados existentes.

### 9.3 POST /receipts/assign

**Request:**
```json
{
  "collector_id": 3,
  "receipt_ids": [10, 11, 12, 13, 14]
}
```

**Validaciones:**
1. El cobrador debe existir y estar activo
2. Solo se asignan recibos con status `unassigned`
3. Respetar `receipt_limit` del cobrador (default 50)
4. Calcular: disponibles = receipt_limit - recibos_activos_actuales
5. Si hay mas recibos que el limite: truncar y avisar

**Conteo de recibos activos:** status IN (`assigned`, `used`, `lost`, `cancelled_undelivered`)

### 9.4 POST /receipts/verify

**Request:**
```json
{
  "receipt_number": "A0023",
  "collector_id": 3,
  "policy_id": 200,
  "payment_id": 500
}
```

**Validaciones secuenciales:**
1. Formato: letra + 4 digitos (ej: A0023)
2. Existencia: el recibo debe existir
3. Propiedad: asignado al cobrador indicado (collector_id debe coincidir)
4. Status valido: debe ser `assigned` (o `used` si es el mismo policy_id/payment_id -> warning)
5. Deteccion de recibos saltados: buscar recibos del mismo cobrador con numero menor aun en `assigned`

**Response:**
```json
{
  "valid": true,
  "receipt": {"id": 23, "receipt_number": "A0023", "status": "assigned"},
  "skipped_receipts": ["A0020", "A0021"],
  "warning": "Se detectaron 2 recibos sin usar antes de este"
}
```

**Extravios programados:** si se detectan recibos saltados y el usuario confirma, se programan para extravio en 3 dias (tabla `receipt_loss_schedule`). Si el recibo se usa antes de los 3 dias, la programacion se cancela.

### 9.5 Maquina de estados del recibo

```
unassigned -> assigned -> used -> delivered
                       \-> lost
                       \-> cancelled_undelivered -> cancelled
```

Transiciones:
- `unassigned -> assigned`: asignar a cobrador
- `assigned -> used`: usar en un cobro (registrar payment_id, policy_id, usage_date)
- `used -> delivered`: entregar fisicamente en oficina (requiere pago con office_delivery = delivered)
- `assigned -> lost`: recibo extraviado (manual o automatico por schedule)
- `assigned/unassigned -> cancelled_undelivered`: cancelar sin entrega
- `used/delivered -> cancelled`: cancelar con posible reversion de pago

### 9.6 Recibos Digitales (Futuro)

Transicion planificada de recibos fisicos impresos a recibos digitales:

- **Recibo digital enviado al cliente via WhatsApp** despues de la confirmacion de pago
- Los recibos fisicos se eliminaran gradualmente conforme se adopte el sistema digital
- El recibo digital incluye:
  - **Codigo QR** para verificacion de autenticidad
  - **Detalles del pago:** monto, fecha, metodo de pago, numero de recibo
  - **Informacion de la poliza:** folio, cobertura, vehiculo, vigencia
- La generacion del recibo digital se dispara automaticamente al marcar un pago como `paid`
- El cliente recibe el recibo en su numero de WhatsApp registrado (via Evolution API)

---

## 10. TARJETAS Y COBRANZA

### 10.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/cards` | Listar tarjetas (paginado) | `cobranza_access` |
| GET | `/cards/:id` | Detalle de tarjeta | `cobranza_access` |
| GET | `/cards/by-policy/:policy_id` | Tarjeta de una poliza | `cobranza_access` |
| POST | `/cards/:id/reassign` | Reasignar a otro cobrador | `cobranza_access` |
| GET | `/cards/:id/history` | Historial de asignaciones | `cobranza_access` |
| GET | `/collections/by-collector/:collector_id` | Cuentas de cobranza | `cobranza_access` |
| GET | `/collections/route` | Ruta de cobranza (PostGIS) | `collector` |
| GET | `/collections/nearby` | Clientes cercanos (PostGIS) | `collector` |
| GET | `/collections/dashboard` | Dashboard de cobranza | `cobranza_access` |

### 10.2 POST /cards/:id/reassign

**Request:**
```json
{
  "assigned_to": "EDGAR",
  "zone": "ZONA NORTE",
  "route": "RUTA 3",
  "observations": "Reasignacion por cambio de zona"
}
```

**Acciones:**
1. Crear registro en `collection_assignment` con nueva asignacion
2. Actualizar `current_holder` en tabla `card`
3. En una sola transaccion

### 10.3 GET /collections/nearby (PostGIS)

**Query params:**
```
?latitude=20.6736
&longitude=-103.3650
&radius_km=5
&status=pending           # status del pago
&limit=50
```

**Response:**
```json
{
  "data": [
    {
      "policy_folio": 18500,
      "client_name": "Juan Perez",
      "address": "Av Vallarta 1234, Americana",
      "distance_meters": 1250,
      "pending_payment": {
        "id": 500,
        "payment_number": 3,
        "amount": "500.00",
        "due_date": "2026-02-15",
        "status": "pending"
      }
    }
  ]
}
```

### 10.4 GET /collections/route (PostGIS)

Calcula la ruta optimizada de cobranza para el cobrador autenticado.

**Response:**
```json
{
  "collector": {"id": 3, "code_name": "EDGAR"},
  "route": [
    {
      "order": 1,
      "policy_folio": 18500,
      "client_name": "Juan Perez",
      "address": "Av Vallarta 1234",
      "latitude": 20.6736,
      "longitude": -103.3650,
      "distance_from_previous_meters": 0,
      "pending_amount": "500.00"
    },
    {
      "order": 2,
      "policy_folio": 18510,
      "client_name": "Maria Garcia",
      "address": "Lopez Mateos 567",
      "latitude": 20.6800,
      "longitude": -103.3700,
      "distance_from_previous_meters": 850
    }
  ],
  "total_stops": 15,
  "total_pending_amount": "12500.00"
}
```

### 10.5 Algoritmo de afinidad (Mejor Ubicacion)

Endpoint: GET `/collections/best-collector/:policy_id`

**Logica preservada del sistema actual:**

Modelo aditivo con ponderacion por recencia. Calcula un puntaje para cada cobrador:

| Factor | Puntos base |
|--------|-------------|
| Mismo cliente | 50 |
| Direccion exacta | 40 |
| Misma colonia | 25 |
| Mismo codigo postal | 15 |
| Penalizacion por carga | -30 * (carga/max_carga) |

**Funcion de decaimiento por recencia:** `peso = exp(-0.003 * dias_transcurridos)`

**Normalizacion de direcciones (expandir abreviaciones):**
```
AV -> AVENIDA, CALZ -> CALZADA, BLVD -> BOULEVARD,
PRIV -> PRIVADA, PROL -> PROLONGACION, AND -> ANDADOR,
CDA -> CERRADA, CARR -> CARRETERA, RET -> RETORNO
```

**Response:**
```json
{
  "recommendations": [
    {"collector_id": 3, "code_name": "EDGAR", "score": 78.5, "reason": "Mismo cliente + zona"},
    {"collector_id": 5, "code_name": "JORGE", "score": 45.2, "reason": "Misma colonia"}
  ]
}
```

### 10.6 Ubicaciones especiales de tarjeta (cuentas de cobranza)

| Ubicacion | Significado |
|-----------|-------------|
| Nombre de cobrador (ej: "EDGAR") | Asignada a ese cobrador |
| "OFICINA" | En oficina, sin cobrador asignado |
| "ARCHIVO" | Poliza liquidada o cancelada |
| "DEPOSITO" | Cliente paga por deposito/transferencia |

**Clasificacion por patron de nombre:**
- `V\d+` (V01, V02) = Vendedores
- `M\d+` (M01) = Ajustadores
- Todo lo demas = Cobradores

---

## 11. EMPLEADOS (Unificado)

En el nuevo sistema, vendedores, cobradores y ajustadores **NO son entidades separadas**. Son **empleados** con flags de rol de negocio (`es_vendedor`, `es_cobrador`, `es_ajustador`). Un mismo empleado puede tener multiples roles simultaneamente.

### 11.1 Endpoints principales

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/employees` | Listar empleados (filtros: role, active, department) | `usuarios_admin` |
| GET | `/employees/:id` | Detalle de empleado (incluye todas las configs de rol) | `usuarios_admin` |
| POST | `/employees` | Crear empleado | `admin` |
| PUT | `/employees/:id` | Actualizar empleado | `admin` |
| GET | `/employees/:id/departments` | Departamentos asignados | `usuarios_admin` |
| PUT | `/employees/:id/departments` | Actualizar asignaciones de departamento | `admin` |
| GET | `/employees/:id/permissions` | Overrides de permisos | `usuarios_admin` |
| PUT | `/employees/:id/permissions` | Actualizar overrides de permisos | `admin` |

### 11.2 Shortcuts por rol de negocio

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/employees/by-role/collectors` | Solo cobradores (es_cobrador=true) | `cobranza_access` |
| GET | `/employees/by-role/sellers` | Solo vendedores (es_vendedor=true) | `polizas_read` |
| GET | `/employees/by-role/adjusters` | Solo ajustadores (es_ajustador=true) | `siniestros_read` |

### 11.3 Endpoints especificos por rol

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/employees/:id/receipts` | Recibos (cobrador) | `cobranza_access` |
| GET | `/employees/:id/cards` | Tarjetas asignadas (cobrador) | `cobranza_access` |
| GET | `/employees/:id/stats` | Estadisticas (varia segun rol) | `cobranza_access` / `polizas_read` |
| GET | `/employees/:id/policies` | Polizas (vendedor) | `polizas_read` |
| GET | `/employees/:id/commissions` | Comisiones (vendedor) | `admin` |
| GET | `/adjusters/shifts` | Calendario de guardias de ajustadores | `siniestros_read` |
| POST | `/adjusters/shifts` | Asignar guardia | `admin` |
| GET | `/adjusters/on-duty` | Ajustador(es) de turno hoy | `siniestros_read` |

### 11.4 POST /employees

**Request:**
```json
{
  "code_name": "EDGAR",
  "full_name": "Edgar Ramirez Gonzalez",
  "phone": "3311234567",
  "telegram_id": 7802431635,
  "es_vendedor": false,
  "es_cobrador": true,
  "es_ajustador": false,
  "rol_sistema_id": 3,
  "receipt_limit": 50,
  "sales_target": null,
  "status": "active",
  "departamentos": [
    {"departamento_id": 3, "es_gerente": false}
  ]
}
```

**Validaciones:**
1. `code_name`: unico, obligatorio
2. `receipt_limit`: default 50, minimo 1 (aplica si es_cobrador=true)
3. `phone`: 10 digitos si se proporciona
4. Al menos un rol de negocio debe estar activo (es_vendedor, es_cobrador, o es_ajustador)
5. `rol_sistema_id`: debe corresponder a un rol valido

### 11.5 GET /employees/:id/commissions

**Response:**
```json
{
  "employee": {"id": 5, "code_name": "V05", "es_vendedor": true},
  "commissions": [
    {
      "coverage": "PLATINO",
      "level": 1,
      "percentage": "15.00"
    },
    {
      "coverage": "AMPLIA",
      "level": 1,
      "percentage": "20.00"
    }
  ]
}
```

### 11.6 POST /adjusters/shifts

**Request:**
```json
{
  "shift_date": "2026-02-15",
  "adjuster_id": 2,
  "shift_order": "first"
}
```

**Ordenes de turno:** first, second, third, rest

**Notificacion automatica a las 09:00** del ajustador de turno por Telegram.

---

## 12. CANCELACIONES

### 12.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/cancellations` | Listar cancelaciones | `polizas_read` |
| GET | `/cancellations/:id` | Detalle de cancelacion | `polizas_read` |
| POST | `/cancellations` | Procesar cancelacion | `polizas_write` |
| POST | `/cancellations/:id/undo` | Deshacer cancelacion | `admin` |
| POST | `/cancellations/:id/notify/:recipient` | Enviar notificacion | `polizas_write` |

### 12.2 POST /cancellations

**Request:**
```json
{
  "policy_id": 200,
  "reason": "Cliente solicita cancelacion",
  "code": "C1",
  "payments_made": 3,
  "update_card": true,
  "observations": "El cliente se mudo de ciudad"
}
```

**Codigos de cancelacion:**
- C1, C2, C3, C4: cancelaciones normales
- C5: tratamiento especial en reportes de renovaciones (resaltado naranja)

**Acciones automaticas:**
1. Validar que la poliza existe y no esta ya cancelada
2. Crear registro en `cancellation`
3. Actualizar poliza: status = `cancelled`
4. Cancelar pagos pendientes: todos los pagos con payment_number > payments_made -> status = `cancelled`
5. Si `update_card = true`: mover tarjeta a ARCHIVO, status = cancelled

### 12.3 POST /cancellations/:id/undo

**Acciones:**
1. Eliminar registro de cancelacion
2. Restaurar pagos cancelados: los pagos marcados como `cancelled` despues de payments_made -> status = `pending`
3. Restaurar tarjeta: mover a "OFICINA"
4. Recalcular status via StatusUpdater

### 12.4 POST /cancellations/:id/notify/:recipient

Donde `:recipient` es `seller`, `collector`, o `client`.

**Logica:**
- `seller`: envia notificacion por Telegram al vendedor de la poliza
- `collector`: envia notificacion por WhatsApp al cobrador
- `client`: envia notificacion por WhatsApp al cliente

Registra `notification_sent_{type} = true` y fecha de notificacion.

---

## 13. RENOVACIONES

### 13.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/renewals` | Listar renovaciones | `polizas_read` |
| GET | `/renewals/pending` | Polizas proximas a vencer | `polizas_read` |
| POST | `/renewals` | Crear renovacion | `polizas_write` |
| GET | `/renewals/report` | Generar reporte Excel | `reportes_read` |
| GET | `/renewals/:id` | Detalle de renovacion | `polizas_read` |

### 13.2 GET /renewals/pending

**Query params:**
```
?days_before=30          # polizas que vencen en los proximos N dias
&days_after=30           # polizas que ya vencieron hace N dias
&seller_id=5             # filtro por vendedor
&coverage_name=PLATINO   # filtro por cobertura
```

**Response:**
```json
{
  "data": [
    {
      "policy_folio": 18500,
      "client_name": "Juan Perez",
      "coverage": "PLATINO",
      "expiration_date": "2026-03-01",
      "days_to_expiration": 15,
      "status": "active",
      "seller": "V05 - Pedro Lopez",
      "eligible_amplia_select": true,
      "cancellation_code": null,
      "has_incidents": false,
      "tow_services_used": 1
    }
  ]
}
```

### 13.3 Notificaciones automaticas de renovacion

4 tipos de notificacion (ejecutadas por scheduler):

| Tipo | Momento | Canal |
|------|---------|-------|
| `renewal_15d` | 15 dias antes de vencimiento | Telegram a vendedor + gerente |
| `renewal_3d` | 3 dias antes de vencimiento | Telegram a vendedor + gerente |
| `expired_7d` | 7 dias despues de vencimiento | Telegram a vendedor + gerente |
| `expired_30d` | 30 dias despues de vencimiento | Telegram a vendedor + gerente |

---

## 14. SINIESTROS

### 14.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/incidents` | Listar siniestros | `siniestros_read` |
| GET | `/incidents/:id` | Detalle de siniestro | `siniestros_read` |
| POST | `/incidents` | Crear reporte de siniestro | `siniestros_write` |
| PUT | `/incidents/:id` | Actualizar siniestro | `siniestros_write` |
| POST | `/incidents/:id/photos` | Subir fotos | `siniestros_write` |
| GET | `/incidents/assigned` | Siniestros asignados (ajustador) | `adjuster` |
| POST | `/incidents/:id/survey` | Registrar encuesta de satisfaccion | `siniestros_write` |
| GET | `/incidents/:id/medical-passes` | Pases medicos del siniestro | `siniestros_read` |
| POST | `/incidents/:id/medical-passes` | Crear pase medico | `siniestros_write` |
| GET | `/incidents/:id/workshop-passes` | Pases de taller | `siniestros_read` |
| POST | `/incidents/:id/workshop-passes` | Crear pase de taller | `siniestros_write` |

### 14.2 POST /incidents

**Request:**
```json
{
  "policy_id": 200,
  "requester_name": "Juan Perez",
  "phone": "3311234567",
  "incident_type": "collision",
  "description": "Choque frontal en cruce",
  "origin_address": {
    "street": "Lopez Mateos 100",
    "neighborhood": "Centro",
    "municipality_id": 5,
    "latitude": 20.67,
    "longitude": -103.36
  },
  "responsibility": "not_responsible",
  "adjuster_id": 2
}
```

**Validaciones de elegibilidad (preservadas):**

Para poliza AMPLIA:
1. **ACTIVA**: permitir
2. **PENDIENTE**: BLOQUEAR. Responder con datos del pago 1 pendiente
3. **MOROSA**: permitir SOLO SI:
   - Pago 1 esta `paid`
   - Solo tiene 1 pago atrasado (no mas)
   - El pago atrasado tiene <= 5 dias (status `late`, no `overdue`)

Deteccion de pago inicial fragmentado: si pago 1 esta `paid` pero su monto < initial_payment de la cobertura, verificar que pago 2 no este vencido.

**Numero de reporte:** generado automaticamente por trigger: `INC-YYYYMMDD-0001`

### 14.3 Tipos de siniestro

```
collision       = Colision
theft           = Robo
total_loss      = Perdida total
vandalism       = Vandalismo
natural_disaster = Desastre natural
other           = Otro
```

---

## 15. GRUAS

### 15.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/tow-services` | Listar servicios de grua | `siniestros_read` |
| GET | `/tow-services/:id` | Detalle de servicio | `siniestros_read` |
| POST | `/tow-services` | Solicitar grua | `siniestros_write` |
| PUT | `/tow-services/:id` | Actualizar servicio | `siniestros_write` |
| POST | `/tow-services/:id/survey` | Encuesta de satisfaccion | `siniestros_write` |
| GET | `/tow-providers` | Listar proveedores | `siniestros_read` |
| GET | `/tow-providers/nearby` | Proveedores cercanos (PostGIS) | `siniestros_read` |
| POST | `/tow-providers` | Crear proveedor | `admin` |
| PUT | `/tow-providers/:id` | Actualizar proveedor | `admin` |

### 15.2 POST /tow-services

**Request:**
```json
{
  "policy_id": 200,
  "requester_name": "Juan Perez",
  "phone": "3311234567",
  "vehicle_failure": "Motor apagado",
  "origin_address": {
    "street": "Periferico Sur 500",
    "latitude": 20.63,
    "longitude": -103.40
  },
  "destination_address": {
    "street": "Taller Mecanico Lopez",
    "latitude": 20.65,
    "longitude": -103.38
  },
  "tow_provider_id": 3
}
```

**Validaciones:**
1. Mismas reglas de elegibilidad que siniestros (AMPLIA: activa/morosa limitada)
2. Verificar servicios de grua disponibles: `tow_services_available > 0`
3. Si no hay servicios disponibles: informar al cliente el costo de grua particular

**Limites de cobertura de grua:**

| Cobertura | Limite |
|-----------|--------|
| AMPLIA | $2,000 |
| AMPLIA SELECT | $2,000 |
| PLATINO | $2,000 |
| PLATINO PLUS | $2,000 |
| AMPLIA (polizas antiguas) | $1,500 |
| Otras (default) | $1,200 |

**Constante UMA:** $117.31

### 15.3 GET /tow-providers/nearby (PostGIS)

**Query params:**
```
?latitude=20.63
&longitude=-103.40
&limit=5
```

Retorna los 5 proveedores de grua activos mas cercanos a la ubicacion del siniestro.

---

## 16. ENDOSOS

### 16.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/endorsements` | Listar endosos | `polizas_read` |
| GET | `/endorsements/:id` | Detalle de endoso | `polizas_read` |
| POST | `/endorsements` | Crear solicitud de endoso | `polizas_write` |
| PUT | `/endorsements/:id` | Actualizar endoso | `polizas_write` |
| POST | `/endorsements/:id/approve` | Aprobar endoso | `admin` |
| POST | `/endorsements/:id/apply` | Aplicar endoso | `admin` |
| POST | `/endorsements/:id/reject` | Rechazar endoso | `admin` |

### 16.2 Tipos de endoso

| Tipo | Descripcion |
|------|-------------|
| `plate_change` | Cambio de placas |
| `vehicle_change` | Cambio de vehiculo |
| `coverage_change` | Cambio de cobertura |
| `contractor_change` | Cambio de contratante |
| `rights_transfer` | Cesion de derechos |

### 16.3 POST /endorsements

**Request:**
```json
{
  "policy_id": 200,
  "endorsement_type": "plate_change",
  "change_details": {
    "old_plates": "JAL-1234",
    "new_plates": "JAL-5678"
  },
  "comments": "Cliente renovo placas"
}
```

El campo `change_details` es JSONB y su estructura varia segun el tipo de endoso.

### 16.4 POST /endorsements/:id/calculate-cost

Calculo automatico del costo del endoso basado en tipo y poliza.

**Permisos:** `polizas_read`

**Response:**
```json
{
  "endorsement_id": 10,
  "endorsement_type": "coverage_change",
  "calculated_cost": "850.00",
  "calculation_details": {
    "remaining_policy_days": 180,
    "coverage_difference": "1200.00",
    "prorated_amount": "850.00"
  }
}
```

**Logica:**
- El sistema calcula automaticamente el costo basado en:
  - Tipo de endoso
  - Periodo restante de la poliza
  - Diferencia de cobertura (si aplica)
  - Tarifas configuradas por tipo de endoso

### 16.5 POST /endorsements/:id/send-whatsapp

Envia los detalles del endoso al cliente via WhatsApp usando la integracion con Evolution API.

**Permisos:** `polizas_write`

**Request:**
```json
{
  "message_type": "endorsement_details"
}
```

**Response:**
```json
{
  "sent": true,
  "message_id": "wamid.HBgLNTIxMzMxMTIzNDU2FQIAEhg...",
  "recipient_phone": "5213311234567"
}
```

**Contenido del mensaje:**
- Detalles del endoso (tipo, cambios realizados)
- Costo calculado
- Status de aprobacion
- Datos de la poliza afectada

---

## 17. PROMOCIONES

### 17.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/promotions` | Listar promociones | `promociones_read` |
| GET | `/promotions/:id` | Detalle de promocion | `promociones_read` |
| POST | `/promotions` | Crear promocion | `promociones_write` |
| PUT | `/promotions/:id` | Actualizar promocion | `promociones_write` |
| GET | `/promotions/active` | Promociones vigentes | `promociones_read` |
| POST | `/promotions/:id/rules` | Agregar regla de descuento | `promociones_write` |
| PUT | `/promotions/:id/rules/:rule_id` | Actualizar regla | `promociones_write` |
| DELETE | `/promotions/:id/rules/:rule_id` | Eliminar regla | `promociones_write` |
| POST | `/promotions/:id/apply` | Aplicar promocion a poliza | `promociones_write` |
| GET | `/promotions/:id/applications` | Polizas con esta promocion | `promociones_read` |
| POST | `/promotions/simulate` | Simular aplicacion (sin guardar) | `promociones_read` |

### 17.2 POST /promotions

**Request:**
```json
{
  "name": "Promocion Mayo 2026",
  "description": "15% de descuento en polizas AMPLIA",
  "status": "active",
  "start_date": "2026-05-01",
  "end_date": "2026-05-31",
  "rules": [
    {
      "discount_type": "percentage",
      "discount_value": "15.00",
      "coverage_ids": [3, 4],
      "vehicle_types": null,
      "description": "15% en AMPLIA y AMPLIA SELECT"
    }
  ]
}
```

### 17.3 POST /promotions/:id/apply

**Request:**
```json
{
  "policy_id": 200
}
```

**Logica de aplicacion:** Ver seccion 24 (Sistema de Promociones Completo).

### 17.4 POST /promotions/simulate

Calcula el descuento SIN aplicarlo. Util para que el usuario vea el resultado antes de confirmar.

**Request:**
```json
{
  "promotion_id": 5,
  "policy_id": 200
}
```

**Response:**
```json
{
  "promotion": {"id": 5, "name": "Promocion Mayo 2026"},
  "policy_folio": 18500,
  "original_total": "4200.00",
  "discount_amount": "630.00",
  "final_total": "3570.00",
  "affected_payments": [
    {"payment_number": 7, "original": "500.00", "new": "0.00", "action": "eliminated"},
    {"payment_number": 6, "original": "500.00", "new": "370.00", "action": "reduced"}
  ]
}
```

---

## 18. COTIZACIONES (INTEGRACION EXTERNA)

Las cotizaciones viven en un sistema EXTERNO en `cotizaciones.protegrt.com`. El CRM solo consume su API.

### 18.1 Endpoints (proxy)

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| POST | `/quotes/validate` | Validar cotizacion externa | `polizas_write` |
| POST | `/quotes/approve` | Aprobar cotizacion externa | `polizas_write` |

### 18.2 POST /quotes/validate

**Request:**
```json
{
  "quote_number": "AUT-DC06BCB1",
  "coverage_type": "AMPLIA",
  "vehicle_type": "AUTOMOVIL"
}
```

**Logica interna:**
1. Llamar a `GET https://cotizaciones.protegrt.com/api/v1/quotes/validate/{quote_number}`
2. Headers: `X-API-Key: {api_key}`, `Content-Type: application/json`
3. Timeout: 10 segundos

**Response:**
```json
{
  "valid": true,
  "quote": {
    "quote_number": "AUT-DC06BCB1",
    "brand": "NISSAN",
    "model_type": "VERSA",
    "model_year": "2024",
    "purchase_price": "250000.00",
    "sale_price": "280000.00",
    "commercial_value": "265000.00",
    "deductibles": {
      "damage": "13250.00",
      "theft": "26500.00"
    }
  }
}
```

**Calculos:**
- `commercial_value = (purchase_price + sale_price) / 2`
- Deducibles: delegados a la logica de PolizaAmpliaDetail (ver seccion 26.5)

### 18.3 POST /quotes/approve

**Request:**
```json
{
  "quote_number": "AUT-DC06BCB1"
}
```

Marca la cotizacion como "aprobada" en el backend externo via `POST /api/v1/quotes/by-number/{quote_number}/approve`.

---

## 19. NOTIFICACIONES

### 19.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/notifications/history` | Historial de mensajes | `admin` |
| POST | `/notifications/send-overdue` | Enviar mensajes a morosos | `cobranza_access` |
| POST | `/notifications/send-reminders` | Enviar recordatorios | `cobranza_access` |
| GET | `/notifications/templates` | Listar plantillas | `admin` |
| PUT | `/notifications/templates/:id` | Editar plantilla | `admin` |
| GET | `/notifications/stats` | Estadisticas de envio | `admin` |

### 19.2 GET /notifications/history

**Query params:**
```
?page=1&page_size=50
&policy_id=200
&message_type=overdue    # overdue, reminder
&channel=whatsapp        # whatsapp, telegram, sms
&date_from=2026-02-01
&date_to=2026-02-14
&delivery_status=sent    # queued, sent, delivered, read, failed
```

### 19.3 POST /notifications/send-overdue

**Request:**
```json
{
  "filters": {
    "coverage": "ALL",
    "holder": "EDGAR",
    "payment_status": "ALL"
  }
}
```

**Logica de morosos (preservada):**

Clientes con pagos `late` o `overdue` que cumplen:
- Pago 1: minimo 5 dias de atraso
- Pagos subsecuentes: minimo 3 dias de atraso

**Frecuencia por folio:**
- Maximo 2 mensajes por semana por folio
- Minimo 3 dias de separacion entre mensajes

Ver seccion 25 para detalles completos del sistema de notificaciones.

---

## 20. REPORTES

> **RESTRICCION DE SEGURIDAD:** Los reportes de CLIENTES no permiten exportacion a Excel/CSV por politica de seguridad. Solo consulta en pantalla. Los demas reportes (renovaciones, cobranza, ventas, etc.) si permiten exportacion a Excel.

### 20.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/reports/renewals` | Reporte de renovaciones (Excel) | `reportes_read` |
| GET | `/reports/collections` | Reporte de cobranza | `reportes_read` |
| GET | `/reports/sales` | Reporte de ventas | `reportes_read` |
| GET | `/reports/payment-proposals` | Reporte de pagos temporales del dia | `gerente` |
| GET | `/reports/overdue-payments` | Reporte de morosos | `reportes_read` |
| GET | `/reports/commissions` | Reporte de comisiones | `admin` |
| GET | `/reports/cancellations` | Reporte de cancelaciones | `reportes_read` |

### 20.2 GET /reports/renewals

**Query params:**
```
?month=2026-03
&seller_id=5
&format=xlsx
```

Genera Excel con 4 hojas (preservado del sistema actual):
1. **Renovaciones**: polizas proximas a vencer o ya vencidas
2. **Endosos**: polizas con endosos
3. **Gruas**: servicios de grua
4. **Siniestros**: siniestros reportados

Polizas con cancelacion C5 se resaltan en naranja. Columna de elegibilidad AMPLIA SELECT incluida.

### 20.3 GET /reports/payment-proposals

**Query params:**
```
?date=2026-02-14
&format=xlsx
```

Genera Excel con columnas: Numero de Recibo, Folio, Monto, Fecha Real, ID Vendedor, Numero de Pago.

---

## 21. DASHBOARD

### 21.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/dashboard/summary` | Resumen general | `dashboard_access` |
| GET | `/dashboard/policies-today` | Polizas del dia | `dashboard_access` |
| GET | `/dashboard/sales-monthly` | Ventas del mes | `dashboard_access` |
| GET | `/dashboard/sales-yearly` | Ventas del anio | `dashboard_access` |
| GET | `/dashboard/top-sellers` | Top vendedores | `dashboard_access` |
| GET | `/dashboard/coverage-breakdown` | Desglose por cobertura | `dashboard_access` |
| GET | `/dashboard/vehicle-types` | Desglose por tipo vehiculo | `dashboard_access` |
| GET | `/dashboard/collection-stats` | Estadisticas de cobranza | `cobranza_access` |

### 21.2 GET /dashboard/summary

**Response:**
```json
{
  "policies_today": 5,
  "policies_this_month": 87,
  "policies_this_year": 1250,
  "active_policies": 4500,
  "morosa_policies": 320,
  "pending_proposals": 15,
  "upcoming_renewals_30d": 180,
  "overdue_payments_total": "125000.00"
}
```

> **Mejora vs sistema actual:** Las estadisticas se obtienen de vistas materializadas (refresh diario) para evitar 7 queries secuenciales al dashboard.

---

## 22. ADMINISTRACION

### 22.1 Endpoints

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/admin/employees` | Listar empleados/usuarios | `usuarios_admin` |
| GET | `/admin/employees/:id` | Detalle de empleado | `usuarios_admin` |
| POST | `/admin/employees` | Crear empleado | `usuarios_admin` |
| PUT | `/admin/employees/:id` | Actualizar empleado | `usuarios_admin` |
| DELETE | `/admin/employees/:id` | Desactivar empleado | `usuarios_admin` |
| GET | `/admin/employees/:id/departments` | Asignaciones de departamento (multi-departamento) | `usuarios_admin` |
| PUT | `/admin/employees/:id/departments` | Actualizar departamentos + flag es_gerente | `usuarios_admin` |
| GET | `/admin/employees/:id/permission-overrides` | Overrides de permisos individuales | `usuarios_admin` |
| PUT | `/admin/employees/:id/permission-overrides` | Conceder/revocar permisos especificos | `usuarios_admin` |
| GET | `/admin/roles` | Listar roles | `usuarios_admin` |
| POST | `/admin/roles` | Crear rol | `usuarios_admin` |
| PUT | `/admin/roles/:id` | Actualizar rol | `usuarios_admin` |
| GET | `/admin/permissions` | Listar permisos | `usuarios_admin` |
| POST | `/admin/roles/:id/permissions` | Asignar permisos a rol | `usuarios_admin` |
| GET | `/admin/departments` | Listar departamentos | `usuarios_admin` |
| GET | `/admin/virtual-locations` | Listar ubicaciones virtuales (OFICINA, ARCHIVO, DEPOSITO) | `usuarios_admin` |
| POST | `/admin/virtual-locations` | Crear ubicacion virtual | `admin` |
| PUT | `/admin/virtual-locations/:id` | Actualizar ubicacion virtual | `admin` |
| GET | `/admin/audit-log` | Log de auditoria | `admin` |
| POST | `/admin/status-update` | Ejecutar StatusUpdater manualmente | `admin` |
| GET | `/admin/config` | Configuracion del sistema | `admin` |
| PUT | `/admin/config` | Actualizar configuracion | `admin` |

### 22.2 POST /admin/status-update

Ejecuta manualmente el StatusUpdater que normalmente corre a medianoche.

**Acciones:**
1. Actualizar status de TODOS los pagos pendientes basandose en fechas actuales
2. Recalcular status de TODAS las polizas basandose en el nuevo status de pagos
3. Registrar en `execution_log`

---

## 23. FLUJO PENDIENTE DE AUTORIZACION (DISENO COMPLETO)

### 23.1 Flujo de polizas (vendedor sube desde app movil)

```
Vendedor (app)           Oficina (web)              Registro final
     |                        |                          |
  1. Captura datos poliza     |                          |
     + fotos contrato         |                          |
     + datos vehiculo/cliente |                          |
     |                        |                          |
  2. POST /authorization/requests |                          |
     type=policy_submission   |                          |
     status=pending           |                          |
     |                        |                          |
     |--- notificacion ------>|                          |
     |                   3. Revisa datos                  |
     |                      status=under_review          |
     |                        |                          |
     |                   4a. Datos correctos?             |
     |                      -> Aprobar                    |
     |                        status=approved             |
     |                        |---- crea poliza real ---->|
     |                        |                     policy creada
     |                        |                     pagos creados
     |                        |                     tarjeta creada
     |                        |                          |
     |                   4b. Datos incorrectos?           |
     |                      -> Rechazar con motivo        |
     |                        status=rejected             |
     |<--- notificacion ------|                          |
     |                        |                          |
  5. Corregir y reenviar      |                          |
     (nueva solicitud)        |                          |
```

### 23.2 Flujo de pagos (cobrador registra desde app movil)

```
Cobrador (app)           Auxiliar (web)           Gerente (web)
     |                        |                        |
  1. Cobra en campo           |                        |
     + GPS + foto recibo      |                        |
     POST /authorization/payments |                     |
     status=pending           |                        |
     |                        |                        |
     |--- notificacion ------>|                        |
     |                   2. Revisa propuesta            |
     |                      status=under_review        |
     |                        |                        |
     |                   3a. Monto < $5,000?            |
     |                      -> Aprueba directo          |
     |                      status=approved             |
     |                      -> Aplica a pago original   |
     |                      status=applied              |
     |                        |                        |
     |                   3b. Monto >= $5,000?           |
     |                      -> Escala a gerente ------->|
     |                        requires_manager=true     |
     |                        |                  4. Revisa
     |                        |                     Aprueba/Rechaza
     |                        |                        |
     |                   5. Aplica a pago original      |
     |                      (sincroniza recibo,         |
     |                       StatusUpdater,             |
     |                       verifica liquidacion,      |
     |                       notifica WhatsApp)         |
     |<--- notificacion ------|                        |
```

### 23.3 Endpoints de autorizacion

| Metodo | Ruta | Descripcion | Permisos |
|--------|------|-------------|----------|
| GET | `/authorization/requests` | Listar solicitudes | `gerente` |
| GET | `/authorization/requests/:id` | Detalle de solicitud | `gerente` |
| POST | `/authorization/requests` | Crear solicitud (desde app) | `seller`, `collector` |
| POST | `/authorization/requests/:id/review` | Iniciar revision | `gerente` |
| POST | `/authorization/requests/:id/approve` | Aprobar solicitud | `gerente` |
| POST | `/authorization/requests/:id/reject` | Rechazar solicitud | `gerente` |
| GET | `/authorization/requests/pending` | Solicitudes pendientes | `gerente` |
| GET | `/authorization/requests/mine` | Mis solicitudes | `seller`, `collector` |

### 23.4 Estados y transiciones

```
pending -> under_review -> approved -> (entidad creada/actualizada)
                        \-> rejected
pending -> cancelled (por el solicitante)
```

### 23.5 Notificaciones del flujo

| Evento | Destinatario | Canal |
|--------|-------------|-------|
| Nueva solicitud | Gerente | Push notification + Telegram |
| Aprobada | Solicitante | Push notification |
| Rechazada | Solicitante | Push notification + motivo |
| Pago aplicado | Cliente | WhatsApp (si cumple condiciones) |
| Pago aplicado | Cobrador | WhatsApp (si metodo = deposit/transfer) |

---

## 24. SISTEMA DE PROMOCIONES (DISENO COMPLETO)

### 24.1 Problemas del sistema actual

El sistema actual SOLO soporta descuentos porcentuales via un campo `porcentaje` en la tabla `promociones`. No existe:
- Meses gratis
- $0 enganche
- Descuento por monto fijo
- Descuento por forma de pago
- Descuento por cobertura
- Referidos

### 24.2 Tipos de descuento soportados

| Tipo | Valor ejemplo | Efecto |
|------|--------------|--------|
| `percentage` | 15.00 | 15% de descuento sobre precio total |
| `fixed_amount` | 500.00 | $500 menos del precio total |
| `free_months` | 2 | Se eliminan 2 pagos (desde el ultimo) |
| `zero_down_payment` | 0 | Enganche = $0 (pago 1 eliminado) |

### 24.3 Estructura de datos

```
promotion (1) ----< promotion_rule (N)
    |
    +----- promotion_application (1 por poliza)
```

Una promocion puede tener MULTIPLES reglas. Ejemplo: "Mayo 2026" puede tener:
- Regla 1: 15% de descuento en PLATINO
- Regla 2: 2 meses gratis en AMPLIA
- Regla 3: $0 enganche para renovaciones

### 24.4 Logica de aplicacion

```python
# Pseudocodigo de aplicacion de promocion
def aplicar_promocion(promotion_id, policy_id):
    promotion = get_promotion(promotion_id)
    policy = get_policy(policy_id)
    payments = get_payments(policy_id)  # ordenados por payment_number DESC

    # 1. Verificar vigencia
    if promotion.start_date and today < promotion.start_date: ERROR
    if promotion.end_date and today > promotion.end_date: ERROR

    # 2. Buscar regla aplicable
    for rule in promotion.rules:
        if not matches_conditions(rule, policy):
            continue

        # 3. Aplicar segun tipo
        if rule.discount_type == "percentage":
            total = sum(p.amount for p in payments)
            discount = total * (rule.discount_value / 100)
            apply_discount_from_last(payments, discount)

        elif rule.discount_type == "fixed_amount":
            apply_discount_from_last(payments, rule.discount_value)

        elif rule.discount_type == "free_months":
            months_to_remove = int(rule.discount_value)
            remove_last_n_payments(payments, months_to_remove)

        elif rule.discount_type == "zero_down_payment":
            payments[0].amount = 0  # Pago 1 = $0
            payments[0].status = "paid"

    # 4. Registrar aplicacion
    create_promotion_application(promotion, policy, discount_applied)
```

### 24.5 Condiciones de elegibilidad

El campo `coverage_ids` (JSONB) filtra por cobertura. El campo `vehicle_types` (JSONB) filtra por tipo de vehiculo. `requires_referral` indica si necesita poliza referente.

### 24.6 Logica descendente de eliminacion de pagos (preservada)

Al aplicar un descuento monetario, se eliminan pagos desde el ultimo hacia el primero:
1. Si monto del pago <= descuento restante: eliminar pago completo (DELETE), restar monto
2. Si monto del pago > descuento restante: reducir monto del pago, descuento restante = 0

### 24.7 Ejemplos concretos

**Ejemplo 1: "Mayo 2026 - 15% en AMPLIA"**
```json
{
  "name": "Mayo 2026",
  "rules": [{
    "discount_type": "percentage",
    "discount_value": "15.00",
    "coverage_ids": [3]
  }]
}
```
Poliza AMPLIA de $7,000 -> descuento $1,050 -> pago 7 ($850) eliminado, pago 6 reducido en $200.

**Ejemplo 2: "2 meses gratis para polizas nuevas"**
```json
{
  "name": "2 Meses Gratis",
  "rules": [{
    "discount_type": "free_months",
    "discount_value": "2"
  }]
}
```
Poliza con 7 pagos -> pagos 6 y 7 eliminados. Quedan 5 pagos.

**Ejemplo 3: "$0 enganche en renovaciones PLATINO"**
```json
{
  "name": "Renovacion Sin Enganche",
  "rules": [{
    "discount_type": "zero_down_payment",
    "discount_value": "0",
    "coverage_ids": [1, 2]
  }]
}
```
Enganche (pago 1) se marca como $0 pagado. Los 6 pagos restantes mantienen su monto.

**Ejemplo 4: "Referidos - 10% descuento a referidor y referido"**
```json
{
  "name": "Programa de Referidos",
  "rules": [{
    "discount_type": "percentage",
    "discount_value": "10.00",
    "requires_referral": true
  }]
}
```
Se aplica a AMBAS polizas: la nueva y la del referidor. El campo `referrer_policy_id` en `promotion_application` vincula las dos.

---

## 25. SISTEMA DE NOTIFICACIONES (DISENO COMPLETO)

### 25.1 Arquitectura

```
[API Endpoint] -> [Cola de mensajes] -> [Worker] -> [Canal externo]
                   (tabla sent_message     |
                    con status=queued)     |
                                           +-> WhatsApp (Evolution API)
                                           +-> Telegram (Bot API)
                                           +-> SMS (proveedor TBD)
                                           +-> Email (futuro)
```

> **Mejora critica vs sistema actual:** Los mensajes NO se envian directamente desde el request HTTP. Se encolan en la tabla `sent_message` con status `queued` y un worker asincrono los procesa. Esto evita bloquear la UI/request y permite reintentos.

### 25.2 Canales

| Canal | Servicio | Configuracion |
|-------|----------|---------------|
| WhatsApp | Evolution API | URL + API Key + Instancia (en variables de entorno) |
| Telegram | Bot API | Bot Token + Chat IDs (en variables de entorno) |
| SMS | Proveedor TBD | API Key (en variables de entorno) |
| Email | SMTP / SES | Configuracion SMTP (futuro) |

### 25.3 Normalizacion de telefono (preservada)

```python
def normalizar_telefono(numero):
    digitos = re.sub(r'\D', '', numero)
    if len(digitos) == 10:
        return "521" + digitos  # Prefijo Mexico
    if len(digitos) == 13 and digitos.startswith("521"):
        return digitos
    return None  # No se puede normalizar
```

Se intenta primero `whatsapp`, luego `phone_additional`. Si ninguno tiene 10+ digitos, no se envia.

### 25.4 Templates por tipo de notificacion

| Tipo | Canal | Template |
|------|-------|----------|
| Pago recibido | WhatsApp | Confirmacion de pago con historial de pagos renderizado |
| Moroso (cobro vencido) | WhatsApp | Aviso de pago vencido con datos del pago |
| Recordatorio (proximo pago) | WhatsApp | Recordatorio previo al vencimiento |
| Cancelacion | Telegram | Notificacion al vendedor |
| Renovacion 15d | Telegram | Aviso al vendedor y gerente ventas |
| Renovacion 3d | Telegram | Aviso urgente al vendedor y gerente |
| Expirada 7d | Telegram | Notificacion post-vencimiento |
| Expirada 30d | Telegram | Ultimo aviso |
| Guardia ajustador | Telegram | Turno del dia a las 09:00 |
| Siniestro reportado | Telegram | Notificacion al grupo de siniestros |
| Pago depositado/transferido | WhatsApp | Aviso al cobrador (SOLO para deposit/transfer) |

### 25.5 Reglas de frecuencia para morosos (preservadas)

| Regla | Valor |
|-------|-------|
| Maximo mensajes por semana por folio | 2 |
| Minimo dias entre mensajes | 3 |
| Dias minimos de atraso - Pago 1 | 5 |
| Dias minimos de atraso - Pagos 2+ | 3 |

### 25.6 Reglas de frecuencia para recordatorios (preservadas)

- Solo para polizas AMPLIA o tarjetas en ubicacion "DEPOSITO"
- Solo para pagos 2+ (NO pago 1)
- Fecha limite entre hoy y 7 dias adelante
- Maximo 2 mensajes por (folio, fecha_pago_objetivo)

| Mensajes previos | Accion |
|-----------------|--------|
| 0 | Enviar si dias_restantes en [5, 4, 3] o es 0 |
| 1 enviado a 3+ dias | Solo enviar el dia de vencimiento |
| 1 enviado dia de vencimiento | No enviar mas |
| 2+ | No enviar mas |

**Tipos de recordatorio:**
- `dias_restantes >= 3` -> "PREVIO"
- `dias_restantes == 0` -> "VENCIMIENTO"
- otro -> "URGENTE"

### 25.7 Reintentos

| Campo | Valor |
|-------|-------|
| max_retries | 3 |
| retry_delay | exponential backoff: 1min, 5min, 15min |
| Accion tras 3 fallos | status = `failed`, registrar error |

### 25.8 Historial y tracking

Cada mensaje queda registrado en `sent_message` con:
- Canal, destinatario, tipo de mensaje
- Status de entrega: queued -> sent -> delivered -> read (o failed)
- external_message_id: ID del mensaje en el servicio externo (para webhooks de delivery status)
- Timestamps de cada transicion

### 25.9 Condiciones para WhatsApp al editar pago (preservadas)

Se envian 3 condiciones simultaneas:
1. `actual_date` tiene valor (se pago)
2. `status` es `paid`
3. El recibo tenia status `assigned` ANTES de la edicion

Si el recibo ya estaba `used` o `delivered` antes, NO se re-envia (evita duplicados).

### 25.10 Modos de imagen en WhatsApp (preservados)

1. Historial de pagos renderizado (imagen PNG con tabla visual)
2. Logo de la empresa
3. Sin imagen (solo texto)

---

## 26. LOGICA DE NEGOCIO MEJORADA

### 26.1 StatusUpdater

| Aspecto | Sistema actual | Sistema nuevo | Justificacion |
|---------|---------------|---------------|---------------|
| Ejecucion | Cron a las 00:00, full-table scan | Cron a las 00:00 + trigger on-demand | Ademas del batch nocturno, se ejecuta on-demand al editar un pago, aplicar propuesta, cancelar, etc. |
| Rendimiento | UPDATE masivo en TODAS las polizas | UPDATE solo polizas con pagos que cambian de status | Indices parciales en PostgreSQL permiten queries eficientes |
| Auditoria | Sin registro de cambios | Trigger de auditoria registra cada cambio de status | Tabla audit_log particionada por mes |
| Notificaciones | No notifica cambios de status | Emitir evento al cambiar de status para trigger de notificaciones | Permite notificar al vendedor cuando una poliza se vuelve morosa |

### 26.2 Generacion de folio

| Sistema actual | Sistema nuevo | Justificacion |
|---------------|---------------|---------------|
| `SELECT MAX(folio) + 1` | PostgreSQL SEQUENCE o `MAX(folio) + 1` con row lock | El MAX+1 tiene race condition si dos usuarios crean polizas simultaneamente. Una SEQUENCE de PostgreSQL o un `SELECT FOR UPDATE` elimina el problema. |

### 26.3 Creacion automatica de pagos

| Sistema actual | Sistema nuevo | Justificacion |
|---------------|---------------|---------------|
| Logica en controlador con SQL directo | Logica en servicio `PaymentService.create_payments_for_policy()` | Separacion de responsabilidades. La logica de creacion de pagos es independiente de la UI. |

**Formas de pago soportadas:**

| Forma de pago | Codigo | Pagos | Calculo |
|---------------|--------|-------|---------|
| Contado | `cash` | 1 | total = cash_price |
| Contado 2 Exhibiciones | `cash_2_installments` | 2 | cada uno = cash_price / 2 |
| Mensual 7 Mensualidades | `monthly_7` | 7 | enganche = initial_payment, mensualidad = (credit_price - initial_payment) / 6 |

> **NOTA CRITICA:** El schema PostgreSQL tiene un ENUM `payment_plan_type` con valores `semester, quarterly, monthly_12` que NO existen en el negocio. Se debe corregir a: `cash, cash_2_installments, monthly_7`.

### 26.4 Validacion de AMPLIA SELECT

| Criterio | Descripcion |
|----------|-------------|
| vehicle_key | Solo 101 (AUTOMOVIL), 103 (PICK UP), 105 (CAMIONETA) |
| Historial renovacion | Requiere poliza anterior del mismo cliente |
| Sin problemas de pago | `eligible_no_payment_issues = true` |
| Sin siniestros | `eligible_no_claims = true` |

### 26.5 Calculo de deducibles (preservado)

| Cobertura | Vehiculo | Danos | Robo |
|-----------|----------|-------|------|
| AMPLIA | Auto/Camioneta | valor_comercial * 5% | valor_comercial * 10% |
| AMPLIA | Motocicleta | valor_comercial * 10% | valor_comercial * 20% |
| AMPLIA SELECT | Todos | valor_comercial * 3% | valor_comercial * 5% |

`valor_comercial = (purchase_price + sale_price) / 2`

### 26.6 Liquidacion automatica

| Sistema actual | Sistema nuevo | Justificacion |
|---------------|---------------|---------------|
| Verificacion post-edicion de pago | Misma logica + trigger en StatusUpdater | Centralizar la verificacion de liquidacion |

Cuando TODOS los pagos de un folio estan `paid`:
1. Tarjeta -> ubicacion "ARCHIVO"
2. Tarjeta -> status `paid_off`
3. Registro en collection_assignment con observaciones "LIQUIDADA"

### 26.7 Operaciones asincronas

| Sistema actual | Sistema nuevo | Justificacion |
|---------------|---------------|---------------|
| TODO sincronico en UI thread | Queries BD: async (SQLAlchemy async). WhatsApp/Telegram: encolados. Reportes Excel: background task. | Evita congelar la interfaz. El sistema web con FastAPI es async por naturaleza. |

### 26.8 Abonos parciales (preservado)

1. monto_abono debe ser entre $0.01 y (monto_original - $0.01)
2. Pago original: amount = abono, status = paid
3. Nuevo pago: amount = saldo, status = pending, misma due_date
4. Si es pago #1: renumerar subsecuentes

### 26.9 Reestructuracion contado a cuotas (preservada)

Solo aplica a polizas con payment_plan = `cash_2_installments`:
1. Obtener credit_price de la cobertura
2. total_pagado = suma de pagos con status = paid
3. saldo = credit_price - total_pagado
4. Crear 6 pagos mensuales: saldo / 6
5. Renumerar pagos
6. Actualizar payment_plan a `monthly_7`

### 26.10 Revision de pagos: flujo completo (preservado + mejorado)

1. Obtener pago seleccionado
2. Capturar status del recibo ANTES de cambios
3. Validar datos (7 validaciones del modulo 4.7)
4. Actualizar pago en BD
5. Sincronizar recibo (assigned->used, used->delivered)
6. StatusUpdater (pagos + poliza)
7. Verificar liquidacion automatica
8. Encolar notificacion WhatsApp (si cumple 3 condiciones)
9. **NUEVO:** Registrar en audit_log

### 26.11 Comisiones

Las comisiones se almacenan en `commission_rate` por rol (seller/collaborator), nivel y cobertura. Se calculan como porcentaje sobre la prima total.

### 26.12 Errores conocidos del schema a corregir

Los siguientes campos del schema PostgreSQL actual necesitan correccion antes de implementar:

| Tabla | Campo | Problema | Correccion |
|-------|-------|----------|------------|
| - | `payment_method_type` ENUM | Valores `card, check` no existen. Faltan `deposit, crucero, konfio, terminal_banorte` | Crear ENUM con: `cash, deposit, transfer, crucero, konfio, terminal_banorte` |
| - | `payment_plan_type` ENUM | Valores `semester, quarterly, monthly_12` no existen | Cambiar a: `cash, cash_2_installments, monthly_7` |
| `policy` | - | Falta campo `prima_total` | Agregar `prima_total NUMERIC(12,2)` |
| `client` | - | Falta campo `rfc` | Agregar `rfc VARCHAR(13)` |
| `collector` | `receipt_limit` | Default es 5, debe ser 50 | Cambiar default a 50 |

---

## APENDICE A: RESUMEN DE ENDPOINTS POR MODULO

| Modulo | Endpoints | Metodos |
|--------|-----------|---------|
| Auth | 8 | POST, GET, PUT |
| Clients | 8 | GET, POST, PUT, DELETE |
| Vehicles | 6 | GET, POST, PUT |
| Coverages | 6 | GET, POST, PUT |
| Policies | 11 | GET, POST, PUT |
| Payments | 9 | GET, POST, PUT |
| Authorization Panel | 14 | GET, POST, PUT |
| Receipts | 9 | GET, POST |
| Cards/Collections | 9 | GET, POST |
| Employees (Unificado) | 19 | GET, POST, PUT |
| Cancellations | 5 | GET, POST |
| Renewals | 5 | GET, POST |
| Incidents | 11 | GET, POST, PUT |
| Tow Services | 8 | GET, POST, PUT |
| Endorsements | 9 | GET, POST, PUT |
| Promotions | 12 | GET, POST, PUT, DELETE |
| Quotes | 2 | POST |
| Notifications | 6 | GET, POST, PUT |
| Reports | 7 | GET |
| Dashboard | 8 | GET |
| Admin | 18 | GET, POST, PUT, DELETE |
| Approval Requests | 8 | GET, POST |
| **TOTAL** | **~198** | |

## APENDICE B: JOBS PROGRAMADOS

| Job | Horario | Descripcion |
|-----|---------|-------------|
| StatusUpdater | 00:00 diario | Actualizar status de pagos y polizas |
| MV Refresh | 00:30 diario | Refrescar vistas materializadas |
| Renewal Notifications | Cada hora | Enviar notificaciones de renovacion |
| Adjuster Shift Notification | 09:00 diario | Notificar turno del dia |
| Message Queue Worker | Cada 30 seg | Procesar cola de mensajes (WhatsApp, Telegram, SMS) |
| Receipt Loss Processor | Cada hora | Procesar extravios programados |
| Audit Partition | Dia 25 mensual | Crear particion de audit_log para siguiente mes |

## APENDICE C: CONSTANTES DEL SISTEMA

| Constante | Valor | Uso |
|-----------|-------|-----|
| UMA_VALUE | 117.31 | Unidad de Medida y Actualizacion |
| TOW_COVERAGE_AMPLIA | 2000 | Limite grua AMPLIA/SELECT/PLATINO |
| TOW_COVERAGE_OLD | 1500 | Limite grua AMPLIA antiguos |
| TOW_COVERAGE_DEFAULT | 1200 | Limite grua otras coberturas |
| PAYMENT_LATE_DAYS | 5 | Dias para pasar de pending a late |
| OVERDUE_MSG_MIN_DAYS_P1 | 5 | Dias minimos atraso pago 1 para moroso msg |
| OVERDUE_MSG_MIN_DAYS_PN | 3 | Dias minimos atraso pagos 2+ para moroso msg |
| OVERDUE_MSG_MAX_PER_WEEK | 2 | Maximo mensajes moroso por semana |
| OVERDUE_MSG_MIN_GAP_DAYS | 3 | Minimo dias entre mensajes moroso |
| REMINDER_DAYS_AHEAD | 7 | Dias anticipacion para recordatorios |
| REMINDER_MAX_PER_TARGET | 2 | Maximo recordatorios por (folio, fecha_pago) |
| RECEIPT_LOSS_DELAY_DAYS | 3 | Dias para programar extravio |
| COLLECTOR_RECEIPT_LIMIT | 50 | Default recibos por cobrador |
| ACCESS_TOKEN_EXPIRY | 900 | Segundos (15 min) |
| REFRESH_TOKEN_EXPIRY | 604800 | Segundos (7 dias) |
| MAX_LOGIN_ATTEMPTS | 5 | Intentos antes de bloqueo |
| LOGIN_LOCKOUT_MINUTES | 15 | Minutos de bloqueo |
| ESCALATION_AMOUNT | 5000 | Monto para escalar a gerente |

## APENDICE D: MAPEO SISTEMA ACTUAL -> NUEVO

| Tabla MySQL actual | Tabla PostgreSQL nueva | Notas |
|-------------------|----------------------|-------|
| polizas | policy | folio como campo negocio, id como PK |
| clientes | client | + address separada + rfc |
| pagos | payment | policy_id en vez de folio FK |
| pagos_temporales | payment_proposal | + flujo de autorizacion |
| recibos_new | receipt | Misma estructura |
| recibos_extravio_programado | receipt_loss_schedule | Sin cambio |
| tarjetas | card | + status enum |
| ubicacion_tarjeta | collection_assignment | Renombrada |
| cancelaciones | cancellation | + timestamps notificacion |
| promociones | promotion + promotion_rule | Estructura flexible |
| cobrador | employee (es_cobrador=true) | Unificado en tabla employee con flags de rol |
| vendedor | employee (es_vendedor=true) | Unificado en tabla employee con flags de rol |
| coverages | coverage | + category enum |
| poliza_amplia_details | policy_amplia_detail | Mismos campos |
| mensajes_enviados | sent_message | + canal + delivery status + reintentos |
| usuarios | app_user | Nombre diferente (reservado) |
| (nueva) | approval_request | Flujo de autorizacion |
| (nueva) | device_session | Apps moviles |
| (nueva) | mobile_action_log | Log acciones moviles |
| (nueva) | promotion_application | Promociones aplicadas |
| (eliminada) | - | promocion_mayo (legacy) |

---

> Documento generado el 2026-02-14. Basado en el analisis completo del INFORME_LOGICA_NEGOCIO.md (1414 lineas, 26 modulos), INFORME_OPTIMIZACION.md, y schema.sql PostgreSQL v2.0.
