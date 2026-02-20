# 10 - API Endpoints: Módulo Cobradores

**Fecha:** 2026-02-20
**Origen:** Sesión de diseño Fer + Claudy
**Estado:** En diseño ✏️
**Stack:** FastAPI + PostgreSQL + PostGIS
**Auth:** JWT Bearer Token (rol embebido en payload)

---

## ÍNDICE

1. [Autenticación](#1-autenticación)
2. [Dashboard del Cobrador](#2-dashboard-del-cobrador)
3. [Folios / Tarjetas Asignadas](#3-folios--tarjetas-asignadas)
4. [Detalle de Póliza](#4-detalle-de-póliza)
5. [Propuestas de Cobro](#5-propuestas-de-cobro)
6. [Abonos Parciales](#6-abonos-parciales)
7. [Avisos de Visita](#7-avisos-de-visita)
8. [Efectivo Pendiente](#8-efectivo-pendiente)
9. [Rutas y Geocodificación](#9-rutas-y-geocodificación)
10. [Notificaciones](#10-notificaciones)
11. [Autorización (Gerente)](#11-autorización-gerente)
12. [Confirmación de Efectivo](#12-confirmación-de-efectivo)
13. [Comisiones](#13-comisiones)
14. [Archivos / Fotos](#14-archivos--fotos)

---

## CONVENCIONES

- **Base URL:** `/api/v1`
- **Auth:** Todas las rutas requieren `Authorization: Bearer <jwt>` excepto `/auth/login`
- **Roles en JWT:** `cobrador`, `gerente_cobranza`, `auxiliar_cobranza`, `admin`
- **Paginación:** `?page=1&per_page=20` (default 20, max 100)
- **Filtros:** query params con prefijo del campo (ej: `?status=pendiente`)
- **Respuestas estándar:**
  ```json
  {
    "ok": true,
    "data": { ... },
    "meta": { "page": 1, "per_page": 20, "total": 145 }
  }
  ```
- **Errores:**
  ```json
  {
    "ok": false,
    "error": "FOLIO_NOT_FOUND",
    "message": "El folio 99999 no existe o no está asignado a este cobrador"
  }
  ```
- **Timestamps:** ISO 8601 con timezone (`2026-02-20T10:15:00-06:00`)
- **Montos:** String con 2 decimales (`"1200.00"`) — evitar floating point

---

## 1. AUTENTICACIÓN

### `POST /auth/login`
Login del cobrador, gerente o auxiliar.

**Request:**
```json
{
  "username": "edgar.ramirez",
  "password": "********"
}
```

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "token": "eyJ...",
    "refresh_token": "eyJ...",
    "user": {
      "id": 12,
      "name": "Edgar Ramírez",
      "role": "cobrador",
      "avatar_url": null
    },
    "expires_at": "2026-02-21T10:00:00-06:00"
  }
}
```

### `POST /auth/refresh`
Renovar token con refresh_token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

### `POST /auth/biometric`
Login por biometría (device_id + biometric_token previamente registrado).

**Request:**
```json
{
  "device_id": "abc123",
  "biometric_token": "stored-hash"
}
```

### `POST /auth/biometric/register`
🔒 **Auth requerida.** Registrar dispositivo para biometría.

**Request:**
```json
{
  "device_id": "abc123",
  "biometric_token": "hash-from-device"
}
```

---

## 2. DASHBOARD DEL COBRADOR

### `GET /cobrador/dashboard`
🔒 **Rol:** `cobrador`

Datos consolidados para la pantalla principal.

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "greeting_name": "Edgar",
    "date": "2026-02-20",
    "cash_pending": {
      "amount": "3250.00",
      "cap": "5000.00",
      "cap_active": true,
      "percentage": 65
    },
    "day_summary": {
      "collections_count": 8,
      "collected_amount": "4100.00",
      "pending_approval_count": 2,
      "commission_today": "820.00"
    },
    "recent_notifications": [
      {
        "id": 501,
        "type": "proposal_approved",
        "title": "Pago F:18501 aprobado",
        "created_at": "2026-02-20T11:30:00-06:00"
      },
      {
        "id": 502,
        "type": "proposal_rejected",
        "title": "Pago F:18405 rechazado",
        "body": "Recibo incorrecto",
        "created_at": "2026-02-20T10:45:00-06:00"
      }
    ],
    "alerts": [
      {
        "type": "rejected_unresolved",
        "message": "Tienes 1 propuesta rechazada sin corregir",
        "proposal_id": 1042
      }
    ]
  }
}
```

---

## 3. FOLIOS / TARJETAS ASIGNADAS

### `GET /cobrador/folios`
🔒 **Rol:** `cobrador`

Lista de folios asignados al cobrador autenticado.

**Query params:**
| Param | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `search` | string | - | Buscar por folio o nombre de cliente |
| `status` | enum | `all` | `all`, `pending`, `overdue`, `collected_today` |
| `sort` | enum | `urgency` | `urgency`, `distance`, `amount` |
| `page` | int | 1 | |
| `per_page` | int | 20 | |
| `lat` | float | - | Latitud actual (para sort=distance) |
| `lng` | float | - | Longitud actual (para sort=distance) |

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "total_assigned": 45,
    "folios": [
      {
        "folio": 18405,
        "client_name": "María López García",
        "client_phone": "3312345678",
        "payment_number": 3,
        "total_payments": 7,
        "amount_due": "1200.00",
        "due_date": "2026-02-05",
        "days_overdue": 15,
        "urgency": "critical",
        "has_proposal_today": false,
        "proposal_status": null,
        "address_short": "Av. Hidalgo 120, Tonalá",
        "lat": 20.6231,
        "lng": -103.2345,
        "distance_km": 2.3
      },
      {
        "folio": 18615,
        "client_name": "Carmen Ruiz",
        "payment_number": 4,
        "total_payments": 7,
        "amount_due": "920.00",
        "due_date": "2026-02-25",
        "days_overdue": 0,
        "urgency": "current",
        "has_proposal_today": false,
        "proposal_status": null,
        "address_short": "Juárez 88, Tonalá",
        "lat": null,
        "lng": null,
        "distance_km": null
      }
    ]
  },
  "meta": { "page": 1, "per_page": 20, "total": 45 }
}
```

**Leyenda `urgency`:**
| Valor | Días de atraso | Color UI |
|-------|---------------|----------|
| `critical` | >15 | 🔴 |
| `overdue` | 5-15 | 🟠 |
| `warning` | 1-5 | 🟡 |
| `current` | ≤0 | 🟢 |
| `collected` | Ya cobrado hoy | ⚫ |

---

## 4. DETALLE DE PÓLIZA

### `GET /cobrador/folios/{folio}`
🔒 **Rol:** `cobrador`

Detalle completo de una póliza para el cobrador.

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "folio": 18405,
    "client": {
      "name": "María López García",
      "phone": "3312345678",
      "address": "Av. Hidalgo 120, Col. Centro, Tonalá, Jalisco",
      "lat": 20.6231,
      "lng": -103.2345
    },
    "vehicle": {
      "brand": "Toyota",
      "model": "Corolla",
      "year": 2020,
      "plates": "ABC-123-D",
      "color": "Blanco"
    },
    "policy": {
      "coverage_type": "AMPLIA",
      "start_date": "2026-02-01",
      "end_date": "2027-02-01",
      "status": "active"
    },
    "current_payment": {
      "payment_number": 3,
      "total_payments": 7,
      "amount_due": "1200.00",
      "amount_paid": "0.00",
      "remaining": "1200.00",
      "due_date": "2026-02-05",
      "days_overdue": 15,
      "partial_payments": []
    },
    "payment_history": [
      {
        "payment_number": 1,
        "amount": "1200.00",
        "paid_date": "2025-12-03",
        "method": "efectivo",
        "status": "applied"
      },
      {
        "payment_number": 2,
        "amount": "1200.00",
        "paid_date": "2026-01-08",
        "method": "transferencia",
        "status": "applied"
      }
    ],
    "can_collect": true,
    "block_reason": null,
    "today_proposal": null
  }
}
```

**`can_collect` = false cuando:**
- Ya existe una propuesta pendiente/aprobada de hoy para este folio
- El cobrador tiene el efectivo bloqueado por tope

---

## 5. PROPUESTAS DE COBRO

### `POST /cobrador/proposals`
🔒 **Rol:** `cobrador`

Registrar una propuesta de cobro completo.

**Request (multipart/form-data):**
```
folio: 18405
payment_number: 3
amount: "1200.00"
method: "efectivo"           ← efectivo | deposito | transferencia
receipt_number: "A00147"
lat: 20.6231
lng: -103.2345
receipt_photo: <file>        ← opcional, imagen JPG/PNG
```

**Response 201:**
```json
{
  "ok": true,
  "data": {
    "proposal_id": 1047,
    "folio": 18405,
    "payment_number": 3,
    "amount": "1200.00",
    "method": "efectivo",
    "receipt_number": "A00147",
    "status": "pending",
    "created_at": "2026-02-20T10:15:00-06:00",
    "receipt_photo_url": "/files/proposals/1047/receipt.jpg"
  }
}
```

**Validaciones:**
| Validación | Error code |
|------------|-----------|
| Folio no asignado a este cobrador | `FOLIO_NOT_ASSIGNED` |
| Ya existe propuesta pendiente/aprobada hoy | `DUPLICATE_PROPOSAL` |
| Monto ≤ 0 | `INVALID_AMOUNT` |
| Método no válido | `INVALID_METHOD` |
| Falta receipt_number | `RECEIPT_REQUIRED` |
| Receipt_number ya usado en otro cobro | `RECEIPT_DUPLICATE` |
| Efectivo bloqueado por tope | `CASH_CAP_EXCEEDED` |

### `GET /cobrador/proposals`
🔒 **Rol:** `cobrador`

Lista de propuestas del cobrador.

**Query params:**
| Param | Tipo | Default |
|-------|------|---------|
| `date` | date | hoy |
| `status` | enum | `all` (pending, approved, corrected, rejected) |
| `page` | int | 1 |

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "date": "2026-02-20",
    "summary": {
      "approved": { "count": 7, "amount": "8400.00" },
      "pending": { "count": 2, "amount": "2250.00" },
      "rejected": { "count": 1, "amount": "0.00" }
    },
    "proposals": [
      {
        "proposal_id": 1047,
        "folio": 18510,
        "client_name": "Roberto Sánchez",
        "payment_number": 1,
        "amount": "1401.00",
        "method": "efectivo",
        "status": "pending",
        "created_at": "2026-02-20T10:15:00-06:00",
        "reviewed_at": null,
        "reviewed_by": null,
        "rejection_reason": null
      },
      {
        "proposal_id": 1042,
        "folio": 18615,
        "client_name": "Carmen Ruiz",
        "payment_number": 4,
        "amount": "920.00",
        "method": "efectivo",
        "status": "rejected",
        "created_at": "2026-02-20T09:30:00-06:00",
        "reviewed_at": "2026-02-20T09:52:00-06:00",
        "reviewed_by": "Elena García",
        "rejection_reason": "Recibo incorrecto (#A0234)"
      }
    ]
  }
}
```

### `POST /cobrador/proposals/{proposal_id}/resubmit`
🔒 **Rol:** `cobrador`

Reenviar propuesta rechazada con correcciones.

**Request (multipart/form-data):**
```
amount: "920.00"              ← puede corregirse
method: "efectivo"
receipt_number: "A00235"      ← recibo correcto
receipt_photo: <file>         ← nueva foto si aplica
```

**Response 201:** (misma estructura que POST /proposals)

**Validaciones:**
- Solo se puede reenviar si status = `rejected`
- El proposal original queda en historial con `status: rejected`
- Se crea una nueva propuesta vinculada (`parent_proposal_id`)

---

## 6. ABONOS PARCIALES

### `POST /cobrador/proposals/partial`
🔒 **Rol:** `cobrador`

Registrar un abono parcial.

**Request (multipart/form-data):**
```
folio: 18405
payment_number: 3
amount: "500.00"
method: "efectivo"
receipt_number: "A00148"
lat: 20.6231
lng: -103.2345
receipt_photo: <file>
```

**Response 201:**
```json
{
  "ok": true,
  "data": {
    "proposal_id": 1048,
    "folio": 18405,
    "payment_number": 3,
    "partial_seq": 2,
    "amount": "500.00",
    "is_partial": true,
    "payment_total": "1200.00",
    "previously_paid": "500.00",
    "remaining_after": "200.00",
    "completes_payment": false,
    "method": "efectivo",
    "receipt_number": "A00148",
    "status": "pending",
    "created_at": "2026-02-20T10:30:00-06:00"
  }
}
```

**Validaciones adicionales:**
| Validación | Error code |
|------------|-----------|
| Monto > saldo pendiente del pago | `AMOUNT_EXCEEDS_REMAINING` |
| Monto ≤ 0 | `INVALID_AMOUNT` |

**Nota:** Si el abono completa el pago (`remaining_after = 0`), el campo `completes_payment: true` y al aprobarse activa cobertura.

---

## 7. AVISOS DE VISITA

### `POST /cobrador/visit-notices`
🔒 **Rol:** `cobrador`

Registrar un aviso de visita.

**Request (multipart/form-data):**
```
folio: 18405
reason: "client_absent"       ← client_absent | no_cash | will_pay_later | other
reason_detail: ""             ← obligatorio solo si reason=other
lat: 20.6231
lng: -103.2345
evidence_photo: <file>        ← OBLIGATORIA
```

**Response 201:**
```json
{
  "ok": true,
  "data": {
    "notice_id": 301,
    "folio": 18405,
    "client_name": "María López García",
    "reason": "client_absent",
    "reason_label": "Cliente no estaba",
    "collector_name": "Edgar Ramírez",
    "created_at": "2026-02-20T11:23:00-06:00",
    "lat": 20.6231,
    "lng": -103.2345,
    "evidence_photo_url": "/files/notices/301/evidence.jpg",
    "print_data": {
      "client_name": "María López García",
      "folio": 18405,
      "coverage": "AMPLIA",
      "vehicle": "Toyota Corolla 2020",
      "payment_number": 3,
      "amount_due": "1200.00",
      "due_date": "2026-02-05",
      "collector_name": "Edgar Ramírez",
      "office_phone": "33-1523-8670",
      "office_hours": "9:00 AM - 3:00 PM (L-V)",
      "whatsapp": "33-XXXX-XXXX",
      "bank_account": "CLABE: XXXX",
      "visit_datetime": "2026-02-20T11:23:00-06:00"
    }
  }
}
```

**Validaciones:**
| Validación | Error code |
|------------|-----------|
| Falta evidence_photo | `PHOTO_REQUIRED` |
| reason=other sin reason_detail | `DETAIL_REQUIRED` |
| Folio no asignado | `FOLIO_NOT_ASSIGNED` |

**`print_data`:** Contiene todos los campos pre-formateados para la impresora Bluetooth. La app usa estos datos para generar el ticket sin lógica adicional.

### `GET /cobrador/visit-notices`
🔒 **Rol:** `cobrador`

Lista de avisos del cobrador.

**Query params:** `date`, `folio`, `page`

---

## 8. EFECTIVO PENDIENTE

### `GET /cobrador/cash-pending`
🔒 **Rol:** `cobrador`

Efectivo acumulado sin entregar a oficina.

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "total_pending": "3250.00",
    "cap": "5000.00",
    "cap_active": true,
    "cap_percentage": 65,
    "is_blocked": false,
    "breakdown": [
      {
        "date": "2026-02-20",
        "items": [
          {
            "proposal_id": 1045,
            "folio": 18405,
            "client_name": "María López",
            "amount": "1200.00",
            "approved_at": "2026-02-20T11:30:00-06:00"
          },
          {
            "proposal_id": 1046,
            "folio": 18502,
            "client_name": "Ana González",
            "amount": "850.00",
            "approved_at": "2026-02-20T11:45:00-06:00"
          }
        ],
        "subtotal": "2050.00"
      },
      {
        "date": "2026-02-19",
        "items": [
          {
            "proposal_id": 1038,
            "folio": 18310,
            "client_name": "Pedro Hernández",
            "amount": "1200.00",
            "approved_at": "2026-02-19T14:00:00-06:00"
          }
        ],
        "subtotal": "1200.00"
      }
    ],
    "delivery_history": [
      {
        "delivery_id": 88,
        "date": "2026-02-18",
        "amount": "2450.00",
        "confirmed_by": "Erika Rodríguez",
        "confirmed_at": "2026-02-18T15:30:00-06:00"
      }
    ]
  }
}
```

---

## 9. RUTAS Y GEOCODIFICACIÓN

### `GET /cobrador/route`
🔒 **Rol:** `cobrador`

Ruta optimizada del día.

**Query params:**
| Param | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `lat` | float | sí | Ubicación actual del cobrador |
| `lng` | float | sí | Ubicación actual del cobrador |
| `date` | date | no | Default: hoy |

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "date": "2026-02-20",
    "total_stops": 12,
    "estimated_distance_km": 28.5,
    "stops": [
      {
        "order": 1,
        "folio": 18405,
        "client_name": "María López",
        "address": "Av. Hidalgo 120, Tonalá",
        "lat": 20.6231,
        "lng": -103.2345,
        "amount_due": "1200.00",
        "status": "completed",
        "distance_from_prev_km": 1.2
      },
      {
        "order": 2,
        "folio": 18502,
        "client_name": "Ana González",
        "address": "Reforma 45, Tonalá",
        "lat": 20.6280,
        "lng": -103.2290,
        "amount_due": "850.00",
        "status": "next",
        "distance_from_prev_km": 0.8
      },
      {
        "order": 3,
        "folio": 18510,
        "client_name": "Roberto Sánchez",
        "address": "Juárez 88, Tonalá",
        "lat": null,
        "lng": null,
        "amount_due": "1401.00",
        "status": "pending",
        "distance_from_prev_km": null
      }
    ]
  }
}
```

**`status` de cada parada:**
- `completed` — ya se registró cobro o aviso hoy
- `next` — siguiente en la ruta
- `pending` — aún no visitado
- `skipped` — cobrador decidió saltar

### `PUT /cobrador/route/reorder`
🔒 **Rol:** `cobrador`

Reordenar paradas manualmente.

**Request:**
```json
{
  "stop_order": [18502, 18405, 18510, 18615]
}
```

### `POST /cobrador/route/notify`
🔒 **Rol:** `cobrador`

Enviar WhatsApp masivo a todos los clientes de la ruta.

**Request:**
```json
{
  "date": "2026-02-20",
  "folios": [18405, 18502, 18510]
}
```

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "sent": 3,
    "failed": 0,
    "messages": [
      { "folio": 18405, "phone": "3312345678", "status": "sent" },
      { "folio": 18502, "phone": "3398765432", "status": "sent" },
      { "folio": 18510, "phone": "3311112222", "status": "sent" }
    ]
  }
}
```

### `POST /cobrador/route/track`
🔒 **Rol:** `cobrador`

Tracking pasivo de ubicación del cobrador (la app envía cada X minutos).

**Request:**
```json
{
  "lat": 20.6250,
  "lng": -103.2310,
  "accuracy_m": 15,
  "timestamp": "2026-02-20T10:30:00-06:00"
}
```

---

## 10. NOTIFICACIONES

### `GET /notifications`
🔒 **Rol:** cualquiera autenticado

**Query params:** `page`, `per_page`, `unread_only` (bool)

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "unread_count": 3,
    "notifications": [
      {
        "id": 501,
        "type": "proposal_approved",
        "title": "Pago aprobado",
        "body": "F:18501 · $1,200 · Pago #3 aprobado por Elena",
        "is_read": false,
        "created_at": "2026-02-20T11:30:00-06:00",
        "action_url": "/proposals/1045",
        "data": {
          "proposal_id": 1045,
          "folio": 18501
        }
      }
    ]
  }
}
```

### `PATCH /notifications/{id}/read`
Marcar como leída.

### `POST /notifications/read-all`
Marcar todas como leídas.

### Push Notifications (FCM)
Los siguientes eventos generan push via Firebase Cloud Messaging:

| Evento | Destino | Payload type |
|--------|---------|-------------|
| Propuesta aprobada | Cobrador | `proposal_approved` |
| Propuesta rechazada | Cobrador | `proposal_rejected` |
| Propuesta corregida por gerente | Cobrador | `proposal_corrected` |
| Nueva tarjeta asignada | Cobrador | `folio_assigned` |
| Ruta del día lista | Cobrador | `route_ready` |
| Tope de efectivo (80%) | Cobrador | `cash_warning` |
| Tope de efectivo (100%) | Cobrador | `cash_blocked` |
| Nueva propuesta pendiente | Gerente | `proposal_pending` |
| Cobrador entregó efectivo | Gerente | `cash_delivery` |

### `POST /devices/register`
Registrar token FCM del dispositivo.

**Request:**
```json
{
  "fcm_token": "dKjL...",
  "device_id": "abc123",
  "platform": "android"
}
```

---

## 11. AUTORIZACIÓN (GERENTE)

### `GET /gerente/dashboard`
🔒 **Rol:** `gerente_cobranza`, `auxiliar_cobranza`

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "greeting_name": "Elena",
    "date": "2026-02-20",
    "pending_count": 5,
    "day_summary": {
      "approved": { "count": 28, "amount": "33600.00" },
      "rejected": { "count": 3 },
      "corrected": { "count": 2 }
    },
    "cash_pending_collectors": [
      {
        "collector_id": 12,
        "collector_name": "Edgar Ramírez",
        "cash_amount": "3250.00"
      },
      {
        "collector_id": 15,
        "collector_name": "Jorge López",
        "cash_amount": "1800.00"
      }
    ],
    "stale_proposals": {
      "count": 1,
      "message": "1 propuesta >48h sin revisar"
    }
  }
}
```

### `GET /gerente/proposals`
🔒 **Rol:** `gerente_cobranza`, `auxiliar_cobranza`

**Query params:**
| Param | Tipo | Default |
|-------|------|---------|
| `status` | enum | `pending` |
| `collector_id` | int | todos |
| `date_from` | date | - |
| `date_to` | date | - |
| `page` | int | 1 |

### `GET /gerente/proposals/{proposal_id}`
🔒 **Rol:** `gerente_cobranza`, `auxiliar_cobranza`

Detalle completo de una propuesta para revisión.

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "proposal_id": 1047,
    "collector": {
      "id": 12,
      "name": "Edgar Ramírez"
    },
    "created_at": "2026-02-20T10:15:00-06:00",
    "submitted": {
      "folio": 18510,
      "client_name": "Roberto Sánchez",
      "payment_number": 1,
      "amount": "1401.00",
      "method": "efectivo",
      "receipt_number": "A00147",
      "receipt_photo_url": "/files/proposals/1047/receipt.jpg",
      "lat": 20.6231,
      "lng": -103.2345,
      "location_label": "Tonalá, Jalisco"
    },
    "expected": {
      "payment_number": 1,
      "amount_due": "1401.00",
      "amount_matches": true,
      "receipt_valid": true,
      "receipt_used_elsewhere": false
    },
    "policy_brief": {
      "folio": 18510,
      "coverage": "AMPLIA",
      "vehicle": "Toyota Rav4 2022",
      "status": "active"
    },
    "validation_flags": []
  }
}
```

**`validation_flags`** (array de alertas automáticas):
```json
[
  { "level": "warning", "code": "AMOUNT_MISMATCH", "message": "Monto difiere del esperado: $1,401 vs $1,200" },
  { "level": "error", "code": "RECEIPT_DUPLICATE", "message": "Recibo A00147 ya fue usado en F:18300" }
]
```

### `POST /gerente/proposals/{proposal_id}/approve`
🔒 **Rol:** `gerente_cobranza`, `auxiliar_cobranza`

**Request:**
```json
{}
```
(Sin body — aprobación directa)

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "proposal_id": 1047,
    "status": "approved",
    "approved_by": "Elena García",
    "approved_at": "2026-02-20T11:30:00-06:00",
    "payment_applied": true,
    "services_activated": true,
    "whatsapp_sent": true
  }
}
```

**Side effects al aprobar:**
1. Pago se aplica en la cuenta del cliente
2. Si es el primer pago completo → se activan servicios de grúa/siniestros
3. Se envía comprobante WhatsApp al cliente
4. Se envía push notification al cobrador
5. Si el método es efectivo → se suma al efectivo pendiente del cobrador

### `POST /gerente/proposals/{proposal_id}/correct`
🔒 **Rol:** `gerente_cobranza`, `auxiliar_cobranza`

Corregir y aprobar en un paso.

**Request:**
```json
{
  "corrections": {
    "amount": "1200.00",
    "receipt_number": "A00148"
  },
  "note": "Cobrador registró monto incorrecto, corregido a $1,200"
}
```

**Response 200:** (similar a approve, con `status: corrected`)

### `POST /gerente/proposals/{proposal_id}/reject`
🔒 **Rol:** `gerente_cobranza`, `auxiliar_cobranza`

**Request:**
```json
{
  "reason": "Recibo incorrecto (#A0234). Verificar número de recibo con el talonario."
}
```

**Validaciones:**
- `reason` es **obligatorio** (no se puede rechazar sin motivo)

---

## 12. CONFIRMACIÓN DE EFECTIVO

### `GET /gerente/cash-deliveries/pending`
🔒 **Rol:** `gerente_cobranza`, `auxiliar_cobranza`

Lista de cobradores con efectivo pendiente.

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "collectors": [
      {
        "collector_id": 12,
        "collector_name": "Edgar Ramírez",
        "expected_amount": "3250.00",
        "proposals": [
          {
            "proposal_id": 1045,
            "folio": 18405,
            "amount": "1200.00"
          },
          {
            "proposal_id": 1046,
            "folio": 18502,
            "amount": "850.00"
          },
          {
            "proposal_id": 1038,
            "folio": 18310,
            "amount": "1200.00"
          }
        ]
      }
    ]
  }
}
```

### `POST /gerente/cash-deliveries`
🔒 **Rol:** `gerente_cobranza`, `auxiliar_cobranza`

Confirmar recepción de efectivo de un cobrador.

**Request:**
```json
{
  "collector_id": 12,
  "received_amount": "3050.00",
  "proposal_ids": [1045, 1046, 1038]
}
```

**Response 201:**
```json
{
  "ok": true,
  "data": {
    "delivery_id": 89,
    "collector_name": "Edgar Ramírez",
    "expected_amount": "3250.00",
    "received_amount": "3050.00",
    "difference": "-200.00",
    "has_debt": true,
    "debt": {
      "debt_id": 14,
      "amount": "200.00",
      "collector_id": 12,
      "description": "Diferencia en entrega de efectivo 2026-02-20",
      "will_deduct_from_commission": true
    },
    "confirmed_by": "Erika Rodríguez",
    "confirmed_at": "2026-02-20T15:30:00-06:00"
  }
}
```

**Regla clave:** El pago del CLIENTE se aplica por el monto COMPLETO. La diferencia es deuda del cobrador.

---

## 13. COMISIONES

### `GET /cobrador/commissions`
🔒 **Rol:** `cobrador`

**Query params:** `period` (current, previous), `date_from`, `date_to`

**Response 200:**
```json
{
  "ok": true,
  "data": {
    "period": "2026-02-01 a 2026-02-20",
    "rate": "10%",
    "gross_commission": "4200.00",
    "deductions": [
      {
        "debt_id": 14,
        "amount": "200.00",
        "description": "Diferencia efectivo 2026-02-20",
        "date": "2026-02-20"
      }
    ],
    "total_deductions": "200.00",
    "net_commission": "4000.00",
    "details": [
      {
        "date": "2026-02-20",
        "folio": 18405,
        "client_name": "María López",
        "amount_collected": "1200.00",
        "commission": "120.00",
        "cash_confirmed": true
      }
    ]
  }
}
```

### `GET /gerente/commissions`
🔒 **Rol:** `gerente_cobranza`, `admin`

Resumen de comisiones de todos los cobradores.

**Query params:** `collector_id`, `period`

---

## 14. ARCHIVOS / FOTOS

### `POST /files/upload`
🔒 **Rol:** cualquiera autenticado

Upload genérico de archivos (fotos de recibos, evidencias).

**Request:** `multipart/form-data` con campo `file`

**Response 201:**
```json
{
  "ok": true,
  "data": {
    "file_id": "a1b2c3",
    "url": "/files/a1b2c3",
    "mime_type": "image/jpeg",
    "size_bytes": 245000
  }
}
```

### `GET /files/{file_id}`
🔒 **Rol:** cualquiera autenticado

Descargar archivo. Retorna el archivo binario con Content-Type correcto.

---

## APÉNDICE: RESUMEN DE ENDPOINTS

### Cobrador (14 endpoints)
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/login` | Login |
| POST | `/auth/refresh` | Refresh token |
| POST | `/auth/biometric` | Login biométrico |
| POST | `/auth/biometric/register` | Registrar biometría |
| GET | `/cobrador/dashboard` | Dashboard principal |
| GET | `/cobrador/folios` | Lista de folios asignados |
| GET | `/cobrador/folios/{folio}` | Detalle de póliza |
| POST | `/cobrador/proposals` | Registrar cobro completo |
| GET | `/cobrador/proposals` | Mis propuestas del día |
| POST | `/cobrador/proposals/{id}/resubmit` | Reenviar propuesta rechazada |
| POST | `/cobrador/proposals/partial` | Registrar abono parcial |
| POST | `/cobrador/visit-notices` | Registrar aviso de visita |
| GET | `/cobrador/visit-notices` | Lista de avisos |
| GET | `/cobrador/cash-pending` | Efectivo pendiente |
| GET | `/cobrador/route` | Ruta optimizada |
| PUT | `/cobrador/route/reorder` | Reordenar ruta |
| POST | `/cobrador/route/notify` | WhatsApp masivo |
| POST | `/cobrador/route/track` | Tracking GPS |
| GET | `/cobrador/commissions` | Mis comisiones |

### Gerente (8 endpoints)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/gerente/dashboard` | Dashboard autorización |
| GET | `/gerente/proposals` | Lista propuestas |
| GET | `/gerente/proposals/{id}` | Detalle propuesta |
| POST | `/gerente/proposals/{id}/approve` | Aprobar |
| POST | `/gerente/proposals/{id}/correct` | Corregir y aprobar |
| POST | `/gerente/proposals/{id}/reject` | Rechazar |
| GET | `/gerente/cash-deliveries/pending` | Efectivo por confirmar |
| POST | `/gerente/cash-deliveries` | Confirmar efectivo |
| GET | `/gerente/commissions` | Comisiones cobradores |

### Comunes (5 endpoints)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/notifications` | Lista notificaciones |
| PATCH | `/notifications/{id}/read` | Marcar leída |
| POST | `/notifications/read-all` | Marcar todas leídas |
| POST | `/devices/register` | Registrar FCM token |
| POST | `/files/upload` | Subir archivo |
| GET | `/files/{file_id}` | Descargar archivo |

**Total: ~28 endpoints**

---

*Documento generado en sesión Fer + Claudy — 2026-02-20*
*Siguiente paso: Modelos de datos (tablas PostgreSQL) para el módulo*
