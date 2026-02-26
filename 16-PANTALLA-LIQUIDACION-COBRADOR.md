# 16 - Pantalla de Liquidación Quincenal (Cobrador)

**Fecha:** 2026-02-26
**Origen:** Sesión de diseño Fer + Claudy (con input de Luna 🌙)
**Estado:** En especificación ✏️
**Plataforma:** App Gerente (React Native + Expo)

---

## CONTEXTO

### ¿Por qué esta pantalla?
Elena (gerente de cobranza) actualmente calcula las comisiones y deducciones de cada cobrador **en Excel**. Esta pantalla centraliza ese proceso en el sistema.

### Periodicidad
- **Cortes quincenales:** día 15 y último del mes
- **Pago:** 1-2 días después de la junta de vendedores

### Lo que NO existe en Legacy
- ❌ Tabla de comisiones de cobranza (solo hay comisiones de VENTA)
- ❌ Historial de liquidaciones
- ❌ Préstamos de moto (registro manual)
- ❌ Cálculo automático de deducciones

### Lo que SÍ existe en Legacy
- ✅ `cargas_combustible` — registro de cargas de gasolina por empleado
- ✅ `pagos` — registro de cobros realizados (para calcular comisiones)

---

## ESPECIFICACIÓN DE PANTALLA

### Ruta
`/gerente/liquidacion/[cobrador_id]`

### Acceso desde
- Pantalla de Comisiones (`/gerente/comisiones`) → tap en un cobrador → abre esta pantalla

---

## WIREFRAME

```
╔══════════════════════════════════════════╗
║ ←  Liquidación                    [...]  ║
╠══════════════════════════════════════════╣
║                                          ║
║  ┌─────────────────────────────────────┐ ║
║  │  [EM]  Edgar Martínez               │ ║
║  │        Cobrador · Nivel 1           │ ║
║  │        Período: 16-28 Feb 2026      │ ║
║  └─────────────────────────────────────┘ ║
║                                          ║
╠══════════════════════════════════════════╣
║  💰 COMISIONES GANADAS                   ║
╠══════════════════════════════════════════╣
║                                          ║
║  Cobranza normal (10%)                   ║
║  12 cobros · $13,200 cobrado             ║
║                            +$1,320.00    ║
║  ─────────────────────────────────────   ║
║  Pagos de contado (5%)                   ║
║  3 cobros · $8,500 cobrado               ║
║                              +$425.00    ║
║  ─────────────────────────────────────   ║
║  Entregas de póliza/endoso ($50 c/u)     ║
║  5 entregas                              ║
║                              +$250.00    ║
║  ─────────────────────────────────────   ║
║                                          ║
║  Subtotal comisiones          $1,995.00  ║
║                                          ║
╠══════════════════════════════════════════╣
║  📉 DEDUCCIONES                          ║
╠══════════════════════════════════════════╣
║                                          ║
║  Gasolina (50% empleado)                 ║
║  8 cargas · $1,200 total                 ║
║                              -$600.00    ║
║  ─────────────────────────────────────   ║
║  Préstamo de moto                        ║
║  Cuota quincenal #4 de 12                ║
║                              -$250.00    ║
║  ─────────────────────────────────────   ║
║  Diferencia de efectivo                  ║
║  Entrega del 22 feb: faltaron $150       ║
║                              -$150.00    ║
║  ─────────────────────────────────────   ║
║                                          ║
║  Subtotal deducciones        -$1,000.00  ║
║                                          ║
╠══════════════════════════════════════════╣
║                                          ║
║  ┌─────────────────────────────────────┐ ║
║  │  NETO A PAGAR                       │ ║
║  │                                     │ ║
║  │              $995.00                │ ║
║  │                                     │ ║
║  └─────────────────────────────────────┘ ║
║                                          ║
║  ┌─────────────────────────────────────┐ ║
║  │  ✓ REGISTRAR PAGO                   │ ║ ← Botón primario
║  └─────────────────────────────────────┘ ║
║                                          ║
║  [Ver historial de liquidaciones]        ║ ← Link secundario
║                                          ║
╚══════════════════════════════════════════╝
```

---

## SECCIONES DETALLADAS

### 1. Header con info del cobrador
- Avatar con iniciales
- Nombre completo
- Rol y nivel
- Período de la liquidación (ej: "16-28 Feb 2026")

### 2. Comisiones Ganadas
Desglose de todas las comisiones del período:

| Tipo | Regla | Cálculo |
|------|-------|---------|
| Cobranza normal | 10% del monto | Suma de pagos confirmados × 0.10 |
| Pago de contado | 5% del monto | Pagos de contado confirmados × 0.05 |
| Cobertura AMPLIA | 0% | No genera comisión |
| Entrega póliza/endoso | $50 fijos | Contador × $50 |

**Reglas de exclusión (NO genera comisión):**
- Transferencia o depósito anticipado (cliente pagó solo)
- Pago directo en oficina (antes de que el cobrador actuara)
- Solo "entrega" sin cobro de dinero (excepto los $50)
- Cobertura AMPLIA

### 3. Deducciones
| Tipo | Fuente de datos | Cálculo |
|------|-----------------|---------|
| Gasolina | `cargas_combustible` | 50% del total de cargas del período |
| Préstamo moto | Nueva tabla `prestamos_empleado` | Cuota fija quincenal según amortización |
| Diferencia efectivo | `entregas_efectivo` | Suma de faltantes no justificados |

### 4. Neto a pagar
```
Neto = Subtotal comisiones - Subtotal deducciones
```

### 5. Acción: Registrar Pago
Al presionar:
1. Muestra modal de confirmación con el monto
2. Pregunta método de pago (efectivo, transferencia)
3. Al confirmar:
   - Crea registro en `liquidaciones` con estado PAGADO
   - Marca todos los cobros del período como "comisión liquidada"
   - Marca cargas de combustible del período como "descontadas"
   - Avanza cuota del préstamo de moto
   - Envía notificación al cobrador (opcional)

### 6. Historial de liquidaciones
Link que abre lista de liquidaciones anteriores del cobrador con:
- Fecha
- Monto neto
- Estado (pagado, pendiente)
- Desglose resumido

---

## MODELO DE DATOS (PostgreSQL)

### Tabla `liquidaciones`
```sql
CREATE TABLE liquidaciones (
    id SERIAL PRIMARY KEY,
    cobrador_id INTEGER REFERENCES empleados(id),
    periodo_inicio DATE NOT NULL,
    periodo_fin DATE NOT NULL,
    
    -- Comisiones
    comision_cobranza DECIMAL(10,2) DEFAULT 0,
    comision_contado DECIMAL(10,2) DEFAULT 0,
    comision_entregas DECIMAL(10,2) DEFAULT 0,
    subtotal_comisiones DECIMAL(10,2) GENERATED ALWAYS AS (
        comision_cobranza + comision_contado + comision_entregas
    ) STORED,
    
    -- Deducciones
    deduccion_gasolina DECIMAL(10,2) DEFAULT 0,
    deduccion_prestamo DECIMAL(10,2) DEFAULT 0,
    deduccion_diferencia DECIMAL(10,2) DEFAULT 0,
    subtotal_deducciones DECIMAL(10,2) GENERATED ALWAYS AS (
        deduccion_gasolina + deduccion_prestamo + deduccion_diferencia
    ) STORED,
    
    -- Total
    neto DECIMAL(10,2) GENERATED ALWAYS AS (
        (comision_cobranza + comision_contado + comision_entregas) -
        (deduccion_gasolina + deduccion_prestamo + deduccion_diferencia)
    ) STORED,
    
    -- Metadata
    status VARCHAR(20) DEFAULT 'pendiente', -- pendiente, pagado
    metodo_pago VARCHAR(20), -- efectivo, transferencia
    fecha_pago TIMESTAMP,
    pagado_por INTEGER REFERENCES empleados(id),
    notas TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Tabla `prestamos_empleado`
```sql
CREATE TABLE prestamos_empleado (
    id SERIAL PRIMARY KEY,
    empleado_id INTEGER REFERENCES empleados(id),
    concepto VARCHAR(100), -- 'Préstamo moto', 'Adelanto', etc.
    monto_total DECIMAL(10,2),
    cuotas_total INTEGER,
    cuotas_pagadas INTEGER DEFAULT 0,
    cuota_quincenal DECIMAL(10,2),
    saldo_pendiente DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'activo', -- activo, liquidado
    fecha_inicio DATE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## ENDPOINTS API

### GET `/api/liquidaciones/preview/{cobrador_id}`
Calcula y devuelve el desglose sin guardar.

**Response:**
```json
{
    "cobrador": { "id": 1, "nombre": "Edgar Martínez", "nivel": 1 },
    "periodo": { "inicio": "2026-02-16", "fin": "2026-02-28" },
    "comisiones": {
        "cobranza": { "cobros": 12, "monto_cobrado": 13200, "comision": 1320 },
        "contado": { "cobros": 3, "monto_cobrado": 8500, "comision": 425 },
        "entregas": { "cantidad": 5, "comision": 250 },
        "subtotal": 1995
    },
    "deducciones": {
        "gasolina": { "cargas": 8, "total": 1200, "deduccion": 600 },
        "prestamo": { "concepto": "Moto", "cuota": 4, "total_cuotas": 12, "deduccion": 250 },
        "diferencias": [
            { "fecha": "2026-02-22", "faltante": 150 }
        ],
        "subtotal": 1000
    },
    "neto": 995
}
```

### POST `/api/liquidaciones`
Registra la liquidación como pagada.

**Body:**
```json
{
    "cobrador_id": 1,
    "periodo_inicio": "2026-02-16",
    "periodo_fin": "2026-02-28",
    "metodo_pago": "efectivo",
    "notas": "Pagado en junta del 1 de marzo"
}
```

### GET `/api/liquidaciones/historial/{cobrador_id}`
Lista de liquidaciones anteriores.

---

## PENDIENTES POR DEFINIR

- [ ] ¿Permitir editar deducciones manualmente antes de liquidar?
- [ ] ¿Notificación automática al cobrador cuando se liquida?
- [ ] ¿Reporte imprimible/PDF de la liquidación?
- [ ] ¿Firma digital del cobrador al recibir?

---

## RELACIÓN CON LEGACY

| Concepto | Legacy | Sistema Nuevo |
|----------|--------|---------------|
| Comisiones de venta | ✅ `comisiones_vendedor` | Se migrará |
| Comisiones de cobranza | ❌ Excel de Elena | ✅ `liquidaciones` |
| Cargas de gasolina | ✅ `cargas_combustible` | Se migrará |
| Préstamos empleado | ❌ Manual | ✅ `prestamos_empleado` |
| Historial liquidaciones | ❌ No existe | ✅ `liquidaciones` |

---

## HISTORIAL

| Fecha | Cambio |
|-------|--------|
| 26 feb 2026 | Especificación inicial — Fer + Claudy |
