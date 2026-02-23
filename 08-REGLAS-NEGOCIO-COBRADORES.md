# 08 - Reglas de Negocio: Módulo de Cobradores y Pagos Móvil

**Fecha:** 2026-02-20
**Origen:** Sesión Q&A con Fer (sesión de diseño)
**Estado:** Definido ✅

---

## ÍNDICE

1. [Recibos Digitales vs Físicos](#1-recibos-digitales-vs-físicos)
2. [Flujo de Cobro en la App](#2-flujo-de-cobro-en-la-app)
3. [Pagos Parciales (Abonos)](#3-pagos-parciales-abonos)
4. [Comprobante WhatsApp al Cliente](#4-comprobante-whatsapp-al-cliente)
5. [Aviso de Visita](#5-aviso-de-visita)
6. [Flujo de Autorización (Gerente)](#6-flujo-de-autorización-gerente)
7. [Elegibilidad de Servicios (Grúas/Siniestros)](#7-elegibilidad-de-servicios-grúassiniestros)
8. [Confirmación de Efectivo en Oficina](#8-confirmación-de-efectivo-en-oficina)
9. [Comisiones de Cobradores](#9-comisiones-de-cobradores)
10. [Rutas Inteligentes y Geocodificación](#10-rutas-inteligentes-y-geocodificación)
11. [Control de Efectivo Acumulado](#11-control-de-efectivo-acumulado)
12. [Descuento por Pronto Pago](#12-descuento-por-pronto-pago)
13. [Features Futuras](#13-features-futuras)

---

## 1. RECIBOS DIGITALES VS FÍSICOS

### Flujo principal (99.9% de los casos)
- El cobro se registra en la app → se genera un **recibo digital automáticamente**
- No hay "asignación de recibo físico" como flujo principal

### Excepciones (recibos físicos)
| Caso | Acción |
|------|--------|
| Sin señal/internet | Cobrador usa talonario físico de respaldo |
| Cobrador a prueba (sin acceso a app aún) | Usa talonario físico hasta obtener acceso |
| Cliente que no quiere digital | Cobrador imprime ticket via impresora Bluetooth |

### Folio de recibo digital
- Formato: `A{NNNNN}` — numeración global correlativa (ej: `A00001`, `A00002`)
- **NUNCA puede quedar en `None`** — todo cobro registrado en app genera su folio automáticamente

---

## 2. FLUJO DE COBRO EN LA APP

### UX del cobrador
1. Cobrador ve su **lista de folios asignados** (pre-cargada via ETL con pólizas vigentes)
2. Selecciona folio → datos de póliza, cliente y monto se auto-llenan
3. Confirma el cobro con una de estas acciones:
   - **[COBRO COMPLETO]** — botón principal, grande y claro
   - **[ABONO PARCIAL]** — para cuando el cliente paga menos del monto completo
4. La propuesta queda en estado **"pendiente de aprobación"**
5. Cobrador recibe push notification cuando la gerente aprueba o rechaza

### Dashboard del cobrador en la app
- 💰 Comisión acumulada del período (solo pagos con efectivo confirmado en oficina)
- 💵 Efectivo acumulado sin depositar (con indicador de proximidad al tope si está activo)
- 📋 Lista de propuestas pendientes / aprobadas / rechazadas del día

---

## 3. PAGOS PARCIALES (ABONOS)

### Modelo de datos
```
payment_number: INTEGER    ← número del pago en el plan (1-7)
partial_seq: INTEGER       ← 1, 2, 3... para cada abono del mismo pago
amount: DECIMAL            ← monto del abono
is_partial: BOOLEAN        ← true si es abono
parent_payment_id: FK      ← referencia al pago original si aplica
```

### Visualización
> Pago **2** · Abono 1 de 2 — $500.00
> Pago **2** · Abono 2 de 2 — $901.50

**NO usar decimales** (ej: 2.1) — problema de precisión en BD.

### Reglas de negocio para abonos
- Un pago con abonos incompletos **NO activa servicios** (ver sección 7)
- El abono que COMPLETA un pago sí puede activar servicios
- Los abonos también pueden ser rechazados por el gerente
- El saldo pendiente (suma de abonos vs monto total) siempre visible en historial

---

## 4. COMPROBANTE WHATSAPP AL CLIENTE

### Contenido confirmado
```
💳 Confirmación de Pago Recibido

Estimado/a [NOMBRE CLIENTE]:

📄 Detalles de la Póliza:
• Folio: [FOLIO]
• Cobertura: [TIPO]
• Status: [STATUS]

🚗 Datos del Vehículo:
• Marca: [MARCA]
• Modelo: [MODELO]
• Año: [AÑO]

💰 Pago Recibido:
• Número de pago: [N]
• Fecha: [FECHA]
• Monto: $[MONTO] MXN
• Método: [EFECTIVO/DEPÓSITO/TRANSFERENCIA]
• Folio de recibo: [FOLIO_DIGITAL]   ← NUEVO

📆 Próximo Pago:
• Fecha límite: [FECHA]
• Monto: $[MONTO] MXN

[Datos de contacto y horario]
```

### Reglas
- ✅ Incluir folio del recibo digital SIEMPRE
- ✅ Incluir método de pago
- ❌ NO incluir saldo total pendiente (solo uso interno)
- El cliente NO recibe comprobante si el folio es incorrecto → mecanismo natural de detección de errores

### Dos notificaciones al cliente por cada pago (definido 23 feb 2026)
El cliente recibe **dos mensajes** en momentos diferentes:

1. **Al momento del cobro** → "Pago recibido — pendiente de aprobación"
   - Se envía cuando el cobrador registra la propuesta
   - Datos: folio, monto, método, fecha
   - Formato: WhatsApp digital O impresión Bluetooth (a elección del cliente)

2. **Al aprobar el pago** → "Pago aprobado / aplicado"
   - Se envía cuando la gerente aprueba (o automáticamente si no hay problemas)
   - Datos: historial de pagos, pago aplicado, próxima fecha pendiente, status de póliza
   - Similar al comprobante actual de Legacy pero mejorado visualmente
   - Detalles del contenido: **por definir**

### Aviso "no activa servicios" (decisión 23 feb 2026)
- El aviso de que un abono parcial NO activa servicios de grúa/siniestros **NO se muestra en la pantalla del cobrador**
- Se incluye en: el ticket impreso y la notificación que recibe el cliente
- Razón: no saturar la pantalla del cobrador con info que es relevante para el cliente, no para él

---

## 5. AVISO DE VISITA

**Feature nueva — NO existe en Legacy.**

### Cuándo se genera
- Cobrador llegó a visitar al cliente y:
  - El cliente no estaba en casa
  - Alguien más abrió y no realizó el pago

### Proceso
1. Cobrador selecciona "Aviso de visita" en la app
2. La app genera el aviso con datos pre-llenados
3. Cobrador imprime via **impresora Bluetooth** (ticket formato papel)
4. Cobrador deja el ticket en la puerta/con quien atendió
5. Cobrador **toma foto** del aviso colocado como evidencia
6. La foto queda registrada en el sistema vinculada al aviso

### Contenido del ticket impreso
```
MUTUALIDAD PROTEG-RT

AVISO DE VISITA

Estimado/a: [NOMBRE CLIENTE]

El día de hoy se realizó una visita a su domicilio
para el cobro de su póliza de seguros.

📄 Datos de su póliza:
• Folio: [FOLIO]
• Cobertura: [TIPO]

🚗 Vehículo asegurado:
• [MARCA] [MODELO] [AÑO]
• (SIN placas ni número de serie por privacidad)

💰 Pago pendiente:
• No. de pago: [N]
• Monto: $[MONTO] MXN
• Fecha límite: [FECHA_LIMITE]

📞 Contáctenos para realizar su pago:
• Tel: 33-1523-8670
• Horario: 9:00 AM - 3:00 PM (L-V)
• WhatsApp: [NÚMERO]

También puede realizar su pago por:
• Depósito: [CUENTA / CLABE]
• Transferencia: [DATOS BANCARIOS]

Atentamente,
[NOMBRE COBRADOR]
ÁREA DE COBRANZA — MUTUALIDAD PROTEG-RT
[FECHA Y HORA DE VISITA]
```

---

## 6. FLUJO DE AUTORIZACIÓN (GERENTE)

### Quién puede autorizar
- Gerente de cobranza (Elena) o auxiliar designada (Erika)

### Pantalla de autorización
- Lista compacta y scaneable: folio | cobrador | monto | método | fecha
- Aprobación **uno por uno** — NO hay "aprobar todos" (riesgo de aprobar errores sin revisar)
- Cada propuesta se expande para ver detalle completo

### Acciones disponibles
| Acción | Cuándo usarla |
|--------|---------------|
| ✅ **APROBAR** | Datos correctos, dinero recibido o en tránsito |
| 🔧 **CORREGIR y APROBAR** | Error menor: mandó como pago completo pero era abono, monto levemente incorrecto |
| ❌ **RECHAZAR** | Error grave: folio equivocado, cobrador confundió al cliente |

### Flujo de rechazo
1. Gerente rechaza + escribe motivo
2. Cobrador recibe **push notification** con el motivo
3. Cobrador puede **reenviar propuesta corregida** desde la app (sin re-visitar al cliente si fue error de captura)
4. La propuesta rechazada queda en historial con estado `rechazado` + motivo + timestamp

### Historial de propuestas
- Toda propuesta (aprobada, corregida, rechazada) queda en BD con trazabilidad completa

---

## 7. ELEGIBILIDAD DE SERVICIOS (GRÚAS/SINIESTROS)

### Regla principal
```
El primer PAGO COMPLETO activa los servicios de grúa y siniestros.
```

### Casos específicos
| Situación | ¿Tiene derecho a servicio? |
|-----------|--------------------------|
| Primer pago completo aplicado | ✅ SÍ |
| Primer pago completo **pendiente de aprobación** | ✅ SÍ — se trata como corriente |
| Solo abono parcial (incompleto) | ❌ NO — como si no hubiera pagado |
| Abono que COMPLETA un pago que lo pone vigente | ✅ SÍ |
| Pago completo en estado "pendiente de aprobación" que lo pondría vigente | ✅ SÍ |

### Implementación
El módulo de elegibilidad de grúas y siniestros debe consultar:
1. ¿Tiene al menos un pago COMPLETO aplicado?
2. ¿Existe alguna propuesta PENDIENTE DE APROBACIÓN que, al aplicarse, lo pondría vigente?
3. Si 1 o 2 es verdadero → conceder servicio

**NUNCA negar servicio si hay una propuesta pendiente que cubriría el pago** — el cobrador ya recibió el dinero, solo falta la aprobación administrativa.

---

## 8. CONFIRMACIÓN DE EFECTIVO EN OFICINA

### Quién confirma
**SOLO el departamento de cobranza:** Erika (auxiliar) o Elena (gerente)
- ❌ El cobrador NUNCA puede confirmar su propia entrega de efectivo

### Flujo
1. Cobrador llega a oficina con efectivo
2. Erika o Elena cuenta el dinero y confirma en sistema: "Recibí $[MONTO]"
3. Si el monto confirmado ≠ monto de la propuesta → el sistema registra la diferencia como **deuda del cobrador**

### Deuda de cobrador
- Si cobrador entregó $1,200 pero la propuesta era $1,401 → deuda: $201
- La deuda queda vinculada al cobrador + folio + fecha
- Se **descuenta automáticamente** de las comisiones del cobrador
- El pago del cliente se aplica POR EL MONTO COMPLETO ($1,401) — el cliente no sufre

---

## 9. COMISIONES DE COBRADORES

### Modelo actual: Básico (10%)
- **10% del monto cobrado** — cada pago donde el efectivo ya fue confirmado en oficina
- La comisión se muestra en tiempo real en la app del cobrador

### Modelo anterior / futuro: Tiered (mantener estructura flexible)
- Sueldo base + comisión escalonada
- Umbrales de efectividad de cobranza
- Niveles que desbloquean mayor % al alcanzar metas
- La tabla `commission_rate` soporta ambos modos desde el inicio

### Regla crítica
- La comisión del cobrador en la app solo muestra pagos **con efectivo ya confirmado en oficina**
- Pagos pendientes de confirmación NO cuentan aún para comisión visible
- Las deudas (diferencias de efectivo) se descuentan del cálculo de comisión

---

## 10. RUTAS INTELIGENTES Y GEOCODIFICACIÓN

### Situación actual
- Legacy no tiene coordenadas para los clientes (MySQL sin PostGIS)
- Cobradores actualmente usan Google Maps por su cuenta para navegar

### Plan de geocodificación
**Fase 1 — ETL batch:**
- Al migrar datos del legacy, intentar geocodificar direcciones via Nominatim (OpenStreetMap, gratuito)
- Dirección en texto (calle + colonia + municipio) → coordenadas (lat, lng)
- Registros sin coordenada confiable → marcados como "pendiente de geocodificación humana"

**Fase 2 — Geocodificación pasiva por cobradores:**
- Cuando el cobrador registra un cobro o aviso de visita en la app, se guarda automáticamente su GPS como coordenadas del cliente
- Sin trabajo extra — la ruta se construye sola conforme los cobradores trabajan

### Feature de rutas en la app
1. Cobrador planea su ruta el día anterior o en la mañana
2. App genera ruta optimizada geográficamente con sus clientes asignados
3. **Botón "Notificar ruta"** → WhatsApp masivo a todos los clientes de la ruta:
   > "Hola [NOMBRE], hoy pasaré a tu domicilio a recoger el pago de tu póliza [FOLIO]. ¡Nos vemos!"
4. La ruta se abre en Google Maps (app externa que ya conocen)

---

## 11. CONTROL DE EFECTIVO ACUMULADO

### Feature en la app del cobrador
El cobrador siempre ve en su pantalla principal:
- 💵 **Efectivo acumulado sin depositar:** $X,XXX
- ⚠️ Barra indicadora de proximidad al tope (si está activo)

### Feature de tope automático (PENDIENTE — discutir con Óscar y Elena)
- Cuando el cobrador acumula más de $X,XXX sin depositar → app bloquea nuevos cobros
- Mensaje: "Para continuar cobrando, realiza un depósito primero"
- **Objetivo:** Reducir riesgo de cobradores con mucho efectivo acumulado
- **Riesgo:** Puede desmotivar o dificultar rutas largas
- **Estado:** Idea en el tintero — NO implementar hasta aprobación de Óscar y Elena

---

## 12. DESCUENTO POR PRONTO PAGO

### Regla
- Cliente que paga por **depósito o transferencia bancaria con 5+ días de anticipación** a su fecha límite → **descuento automático** en el monto del pago

### Lógica
- `fecha_limite - fecha_pago >= 5 días` Y `método IN ('depósito', 'transferencia')` → aplica descuento
- El porcentaje de descuento debe ser configurable (no hardcodeado)
- El descuento se registra en el pago y aparece en el comprobante

### Contexto de negocio
- Esta es la razón principal por la que algunos clientes prefieren pagar solos (sin cobrador)
- Los clientes que van por sí solos a depositar/transferir son minoría — la mayoría prefiere cobrador en efectivo

---

## 13. FEATURES FUTURAS

### Portal de clientes + pagos en línea (muy largo plazo)
- Acceso para clientes a ver su historial de pólizas y pagos
- Pago en línea via Stripe u otro procesador
- **Contexto:** La mayoría de clientes de Proteg-rt no son tech-savvy. Esta feature es para el largo plazo.
- **Estado:** Idea confirmada pero post-funcionalidad completa del sistema

---

## RESUMEN DE ROLES Y PERMISOS RELEVANTES

| Acción | Rol permitido |
|--------|--------------|
| Registrar cobro en app | Cobrador |
| Registrar abono parcial en app | Cobrador |
| Registrar aviso de visita | Cobrador |
| Ver sus comisiones | Cobrador |
| Ver efectivo acumulado | Cobrador |
| Planear y notificar ruta | Cobrador |
| Aprobar / Corregir / Rechazar propuesta | Gerente Cobranza, Auxiliar designada |
| Confirmar recepción de efectivo en oficina | Gerente Cobranza, Auxiliar designada |
| Ver deudas de cobrador | Gerente Cobranza |
| Configurar tope de efectivo | Admin |
| Configurar % descuento pronto pago | Admin |
| Configurar comisiones | Admin |

---

*Documento generado en sesión de diseño Fer + Claudy — 2026-02-20*
*Siguiente paso: Diseño de pantallas y endpoints API para módulo cobradores*
