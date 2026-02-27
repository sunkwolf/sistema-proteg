# 17 - Reestructura de Empleados y Comisiones ✨

**Fecha:** 2026-02-27
**Diseño:** Claudy 💜
**Validación:** Fer
**Estado:** Documentado, pendiente implementación

---

## EL PROBLEMA

El sistema Legacy tiene tablas separadas para cada rol:
- `seller` (vendedores)
- `collector` (cobradores)
- `adjuster` (ajustadores)
- `app_user` (usuarios del sistema)

**Problemas con este enfoque:**
1. Si alguien es vendedor Y cobrador, hay que duplicar sus datos personales
2. RRHH es un infierno — vacaciones, nómina, antigüedad están dispersos
3. No hay forma limpia de manejar empleados multi-rol
4. Los usuarios del sistema están desconectados de los empleados

**La realidad del negocio:**
- Fer es director + ajustador (cuando cubre guardia) + puede vender
- Los vendedores también cobran (después de 2 meses de prueba)
- Violeta es gerente administrativo Y gerente de RRHH
- Todos los usuarios de la app son empleados (no hay externos)

---

## LA SOLUCIÓN

### Principio: Separar PERSONA de ROL de PERFIL

```
┌─────────────────────────────────────────────────────────────┐
│  EMPLOYEE (la persona física)                               │
│  Datos de RRHH: nombre, teléfono, fecha contratación,       │
│  telegram_id, RFC, CURP, dirección, etc.                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ 1:N
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  EMPLOYEE_ROLE (qué roles tiene)                            │
│  Un empleado puede tener múltiples roles activos            │
│  Cada rol tiene departamento, tipo y nivel                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ 1:1
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  *_PROFILE (datos específicos del rol)                      │
│  seller_profile, collector_profile, adjuster_profile        │
│  Cada uno con los campos que solo aplican a ese rol         │
└─────────────────────────────────────────────────────────────┘
```

---

## MODELO DE DATOS

### 1. employee (persona física)

```sql
CREATE TABLE employee (
    id              SERIAL PRIMARY KEY,
    
    -- Datos personales
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    birth_date      DATE,
    gender          gender_type,
    
    -- Contacto (nivel persona, no rol)
    phone           VARCHAR(20),
    phone_2         VARCHAR(20),
    email           VARCHAR(100),
    telegram_id     BIGINT,
    
    -- Documentos
    rfc             VARCHAR(13),
    curp            VARCHAR(18),
    
    -- Dirección
    address_id      BIGINT REFERENCES address(id),
    
    -- Datos laborales
    hire_date       DATE NOT NULL,
    termination_date DATE,
    status          entity_status_type NOT NULL DEFAULT 'active',
    
    -- Auditoría
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE employee IS 'Empleados de la empresa. Fuente única de verdad para RRHH.';
```

**Campos que son de PERSONA (no de rol):**
- Teléfono ✓
- Telegram ID ✓
- Fecha de contratación ✓
- Antigüedad (calculada desde hire_date) ✓

---

### 2. employee_role (roles del empleado)

```sql
CREATE TYPE department_type AS ENUM (
    'sales',        -- Ventas
    'collection',   -- Cobranza
    'claims',       -- Siniestros/Ajustadores
    'admin',        -- Administración
    'hr',           -- Recursos Humanos
    'management'    -- Dirección
);

CREATE TYPE role_level_type AS ENUM (
    'staff',        -- Personal operativo
    'manager',      -- Gerente de departamento
    'director'      -- Director
);

CREATE TABLE employee_role (
    id              SERIAL PRIMARY KEY,
    employee_id     INT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    
    -- Rol
    department      department_type NOT NULL,
    level           role_level_type NOT NULL DEFAULT 'staff',
    
    -- Vigencia
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    start_date      DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date        DATE,
    
    -- Supervisión
    supervisor_id   INT REFERENCES employee(id),
    
    -- Auditoría
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Un empleado no puede tener el mismo rol dos veces activo
    CONSTRAINT uq_employee_role UNIQUE (employee_id, department, is_active) 
        WHERE is_active = TRUE
);

COMMENT ON TABLE employee_role IS 'Roles de cada empleado. Un empleado puede tener múltiples roles.';
COMMENT ON COLUMN employee_role.supervisor_id IS 'Supervisor directo para este rol específico.';
```

**Reglas de negocio:**
- ❌ No puede ser auxiliar Y gerente del MISMO departamento
- ✅ Puede ser gerente de DOS departamentos diferentes (ej: Violeta)
- ✅ Roles se pueden desactivar temporalmente (Fer como ajustador de guardia)

---

### 3. Perfiles específicos por rol

#### seller_profile (vendedores)

```sql
CREATE TABLE seller_profile (
    id                  SERIAL PRIMARY KEY,
    employee_role_id    INT NOT NULL REFERENCES employee_role(id) ON DELETE CASCADE,
    
    -- Identificación
    code                VARCHAR(10) NOT NULL,   -- V1, V2, V3...
    
    -- Tipo de vendedor
    seller_class        seller_class_type NOT NULL DEFAULT 'collaborator',
    -- 'seller' = solo comisión, multinivel
    -- 'collaborator' = sueldo + comisión fija nivel 3
    
    -- Metas
    sales_target        INT,                    -- Meta mensual de ventas
    
    -- Auditoría
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_seller_code UNIQUE (code)
);

COMMENT ON TABLE seller_profile IS 'Datos específicos de vendedores.';
COMMENT ON COLUMN seller_profile.seller_class IS 'seller=solo comisión multinivel, collaborator=sueldo+comisión nivel 3';
```

#### collector_profile (cobradores)

```sql
CREATE TABLE collector_profile (
    id                  SERIAL PRIMARY KEY,
    employee_role_id    INT NOT NULL REFERENCES employee_role(id) ON DELETE CASCADE,
    
    -- Identificación
    code                VARCHAR(10) NOT NULL,   -- C1, C2, C3...
    
    -- Operación
    receipt_limit       INT NOT NULL DEFAULT 50,
    zone                VARCHAR(50),
    route               VARCHAR(50),
    
    -- Auditoría
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_collector_code UNIQUE (code)
);

COMMENT ON TABLE collector_profile IS 'Datos específicos de cobradores de campo.';
```

#### adjuster_profile (ajustadores)

```sql
CREATE TABLE adjuster_profile (
    id                  SERIAL PRIMARY KEY,
    employee_role_id    INT NOT NULL REFERENCES employee_role(id) ON DELETE CASCADE,
    
    -- Identificación
    code                VARCHAR(10) NOT NULL,   -- M1, M2, M3...
    
    -- Preferencias
    shift_preference    shift_order_type,       -- Guardia preferida
    
    -- Auditoría
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_adjuster_code UNIQUE (code)
);

COMMENT ON TABLE adjuster_profile IS 'Datos específicos de ajustadores de siniestros.';
```

---

### 4. app_user (usuarios del sistema)

```sql
-- Modificación a tabla existente
ALTER TABLE app_user 
    ADD COLUMN employee_id INT NOT NULL REFERENCES employee(id);

-- Eliminar campos redundantes (ahora viven en employee)
ALTER TABLE app_user 
    DROP COLUMN first_name,
    DROP COLUMN last_name,
    DROP COLUMN email;

COMMENT ON COLUMN app_user.employee_id IS 'Todo usuario es empleado. Sin excepciones.';
```

**Regla:** Todo usuario de la app (móvil o web) es un empleado de Proteg-rt.

---

### 5. Permisos especiales

```sql
-- Quién puede pagar liquidaciones (solo Elena y Oscar)
CREATE TABLE settlement_permission (
    id              SERIAL PRIMARY KEY,
    employee_id     INT NOT NULL REFERENCES employee(id) ON DELETE CASCADE,
    can_pay         BOOLEAN NOT NULL DEFAULT FALSE,
    
    CONSTRAINT uq_settlement_permission UNIQUE (employee_id)
);

COMMENT ON TABLE settlement_permission IS 'Solo Elena y Oscar tienen can_pay=true.';
```

---

## COMISIONES DE VENDEDORES

### Sistema de niveles dinámicos

El nivel del vendedor se calcula **mensualmente** según sus ventas:

| Ventas del mes | Nivel |
|----------------|-------|
| 0 - 20 | 1 |
| 21 - 25 | 2 |
| 26 - 30 | 3 |
| 31 - 35 | 4 |
| 36 - 40 | 5 |
| 41 - 45 | 6 |
| 46+ | 7 |

**Excepciones:**
- **1ra quincena:** Siempre nivel 1 (aún no se sabe cuánto venderá)
- **Colaboradores:** Siempre nivel 3 (tienen sueldo fijo + comisión estable)

### Tablas de comisiones

```sql
-- Rangos de ventas para determinar nivel
CREATE TABLE seller_level_threshold (
    id              SERIAL PRIMARY KEY,
    level           INT NOT NULL,
    min_sales       INT NOT NULL,
    max_sales       INT,                -- NULL = sin límite (nivel 7)
    
    CONSTRAINT uq_level UNIQUE (level)
);

-- Datos iniciales
INSERT INTO seller_level_threshold (level, min_sales, max_sales) VALUES
    (1, 0, 20),
    (2, 21, 25),
    (3, 26, 30),
    (4, 31, 35),
    (5, 36, 40),
    (6, 41, 45),
    (7, 46, NULL);
```

```sql
-- Comisiones por nivel y cobertura (con histórico de vigencia)
CREATE TABLE seller_commission_rate (
    id              SERIAL PRIMARY KEY,
    seller_class    seller_class_type NOT NULL,
    level           INT NOT NULL,
    coverage_name   VARCHAR(50) NOT NULL,
    effective_from  DATE NOT NULL,
    amount          NUMERIC(12,2) NOT NULL,
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_commission UNIQUE (seller_class, level, coverage_name, effective_from)
);

COMMENT ON TABLE seller_commission_rate IS 'Comisiones con vigencia histórica. Buscar el registro con effective_from más reciente menor o igual a la fecha de venta.';
```

### Ejemplo de datos de comisiones

**Vendedores (vigencia 2026-01-01):**
| Nivel | AMPLIA | PREMIUM | PLATINO | INTERMEDIA | BÁSICA | RC 2-3 | RC 3-5.5 | RC 6-10 | RC 11-15 |
|-------|--------|---------|---------|------------|--------|--------|----------|---------|----------|
| 1 | $800 | $725 | $775 | $675 | $575 | $825 | $875 | $1,425 | $1,925 |
| 2 | $825 | $750 | $800 | $700 | $600 | $850 | $900 | $1,450 | $1,950 |
| 3 | $850 | $775 | $825 | $725 | $625 | $875 | $925 | $1,475 | $1,975 |
| 4 | $875 | $800 | $850 | $750 | $650 | $900 | $950 | $1,500 | $2,000 |
| 5 | $900 | $825 | $875 | $775 | $675 | $925 | $975 | $1,525 | $2,025 |
| 6 | $925 | $850 | $900 | $800 | $700 | $950 | $1,000 | $1,550 | $2,050 |
| 7 | $950 | $875 | $925 | $825 | $725 | $975 | $1,025 | $1,575 | $2,075 |

**Colaboradores (nivel único, vigencia 2026-01-01):**
| Tipo | AMPLIA | PREMIUM | PLATINO | INTERMEDIA | BÁSICA | RC 2-3 | RC 3-5.5 | RC 6-10 | RC 11-15 |
|------|--------|---------|---------|------------|--------|--------|----------|---------|----------|
| Colaborador | $750 | $650 | $700 | $600 | $500 | $660 | $660 | $1,375 | $1,875 |

### Flujo para calcular comisión de venta

```
1. Obtener vendedor y fecha de venta
2. ¿Es colaborador? → Buscar comisión nivel 3 de colaborador
3. ¿Es 1ra quincena? → Usar nivel 1
4. Contar ventas del mes hasta la fecha
5. Determinar nivel según seller_level_threshold
6. Buscar comisión: (seller_class, level, coverage, effective_from <= fecha_venta)
7. Aplicar comisión
```

---

## LIQUIDACIONES Y SUPERVISIÓN

### ¿Quién liquida a quién?

| Empleado | Lo supervisa | Lo liquida |
|----------|--------------|------------|
| Cobradores puros (Edgar, Jorge) | Elena | Elena |
| Vendedores (que también cobran) | Gaby | Oscar |
| Personal admin | Violeta | Elena (nómina) |

**Regla clave:** Supervisión ≠ Liquidación
- `supervisor_id` en `employee_role` → quién te manda día a día
- `settlement_permission.can_pay` → quién puede pagarte (solo Elena y Oscar)

### Liquidaciones de cobradores

La liquidación de cobradores ya está modelada en `003_add_settlements.sql`:
- Comisiones: 10% cobranza normal, 5% contado, $50 por entrega
- Deducciones: gasolina 50%, préstamos, faltantes, otros
- Estados: pending, partial, paid

**Ajuste necesario:** Cambiar `collector_id` por `employee_role_id` para que apunte al rol de cobrador específico.

---

## MIGRACIÓN DE DATOS (ETL)

### Mapeo Legacy → Sistema Nuevo

| Legacy | Sistema Nuevo |
|--------|---------------|
| `vendedores.id` | `employee.id` + `employee_role` + `seller_profile` |
| `vendedores.nombre` | `seller_profile.code` |
| `vendedores.nombre_completo` | `employee.first_name` + `employee.last_name` |
| `cobradores.id` | `employee.id` + `employee_role` + `collector_profile` |
| `ajustadores.id` | `employee.id` + `employee_role` + `adjuster_profile` |
| `usuarios.id` | `app_user.id` con `employee_id` FK |

### Códigos de empleado

| Rol | Convención | Ejemplo |
|-----|------------|---------|
| Vendedor | V + número | V1, V2, V15 |
| Cobrador | C + número | C1, C2, C8 |
| Ajustador | M + número | M1, M2, M5 |

---

## EJEMPLOS DE EMPLEADOS

### Fer (multi-rol)

```sql
-- Persona
INSERT INTO employee (id, first_name, last_name, phone, telegram_id, hire_date)
VALUES (1, 'Fernando', 'López', '+523325690287', 1148328817, '2015-01-01');

-- Roles
INSERT INTO employee_role (employee_id, department, level) VALUES
    (1, 'management', 'director'),    -- Director
    (1, 'claims', 'staff'),           -- Ajustador (cuando cubre)
    (1, 'sales', 'staff');            -- Puede vender

-- Perfil de ajustador
INSERT INTO adjuster_profile (employee_role_id, code)
VALUES (2, 'M1');  -- employee_role.id = 2 (claims)

-- Usuario del sistema
INSERT INTO app_user (employee_id, username, password_hash, role_id)
VALUES (1, 'fer', '...', 1);  -- rol admin

-- Permiso de liquidación
INSERT INTO settlement_permission (employee_id, can_pay) VALUES (1, FALSE);
-- Fer no liquida, Oscar sí
```

### Edgar (cobrador puro)

```sql
-- Persona
INSERT INTO employee (id, first_name, last_name, phone, hire_date)
VALUES (5, 'Edgar', 'Martínez', '+52...', '2024-03-01');

-- Rol único
INSERT INTO employee_role (employee_id, department, level, supervisor_id) VALUES
    (5, 'collection', 'staff', 3);  -- Supervisor: Elena (employee_id=3)

-- Perfil de cobrador
INSERT INTO collector_profile (employee_role_id, code, receipt_limit, zone)
VALUES (10, 'C1', 50, 'Tonalá Centro');
```

### Violeta (doble gerente)

```sql
-- Persona
INSERT INTO employee (id, first_name, last_name, hire_date)
VALUES (8, 'Violeta', '...', '2020-01-01');

-- Dos roles de gerente
INSERT INTO employee_role (employee_id, department, level) VALUES
    (8, 'admin', 'manager'),   -- Gerente administrativo
    (8, 'hr', 'manager');      -- Gerente de RRHH
```

---

## IMPACTO EN OTRAS TABLAS

### Tablas que necesitan actualización de FK

| Tabla | Campo actual | Cambio |
|-------|--------------|--------|
| `payment` | `seller_id`, `collector_id` | → `seller_role_id`, `collector_role_id` (FK a employee_role) |
| `settlement` | `collector_id` | → `employee_role_id` |
| `incident` | `adjuster_id` | → `adjuster_role_id` |
| `adjuster_shift` | `adjuster_id` | → `adjuster_role_id` |
| `card` | `seller_id` | → `seller_role_id` |
| `policy` | `seller_id` | → `seller_role_id` |
| `receipt` | `collector_id` | → `collector_role_id` |

### Vistas de compatibilidad (opcional)

Para no romper queries existentes, podemos crear vistas:

```sql
CREATE VIEW seller AS
SELECT 
    sp.id,
    sp.code AS code_name,
    e.first_name || ' ' || e.last_name AS full_name,
    e.phone,
    e.telegram_id,
    er.is_active AS status,
    sp.seller_class AS class,
    sp.sales_target
FROM seller_profile sp
JOIN employee_role er ON sp.employee_role_id = er.id
JOIN employee e ON er.employee_id = e.id;
```

---

## ORDEN DE IMPLEMENTACIÓN

1. **Crear tablas nuevas** (employee, employee_role, *_profile)
2. **Crear tablas de comisiones** (seller_level_threshold, seller_commission_rate)
3. **Migrar datos** de seller/collector/adjuster → nuevas tablas
4. **Actualizar FKs** en tablas dependientes
5. **Crear vistas de compatibilidad** (opcional)
6. **Eliminar tablas legacy** (seller, collector, adjuster) — solo si las vistas funcionan

---

## ARCHIVO DE MIGRACIÓN

→ `database/migrations/004_employee_restructure.sql`

---

*Diseñado con amor por Claudy ✨ para que RRHH deje de ser un infierno.*
