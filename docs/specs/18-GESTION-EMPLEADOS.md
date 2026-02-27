# 📋 Especificación: Módulo Gestión de Empleados

**Estado:** Diseño Inicial ✨
**Diseño:** Claudy
**Arquitectura:** Persona → Rol → Perfil

## 1. Visión General
Elena y Óscar necesitan un lugar centralizado para gestionar al equipo. Ya no queremos datos duplicados si alguien tiene dos funciones.

## 2. Pantalla: Lista de Empleados (`/mobile/app/(gerente)/empleados/index.tsx`)
- **Buscador:** Por nombre o código de empleado.
- **Filtros rápidos:** Todos, Activos, Inactivos, Por Rol (Vendedores, Cobradores, Ajustadores).
- **Cards de Empleado:**
  - Avatar con iniciales y color distintivo (nuestra paleta morado/dorado).
  - Nombre completo.
  - Badges de roles activos (ej: `Vendedor` en verde, `Cobrador` en azul).
  - Indicador de antigüedad.

## 3. Pantalla: Ficha del Empleado (`/mobile/app/(gerente)/empleados/[id].tsx`)
Organizada en pestañas o secciones colapsables:

### A. Información Personal (RRHH)
- Código de empleado, RFC, CURP.
- Fecha de ingreso, estatus (Activo/Baja).
- Datos de contacto.

### B. Roles y Configuración
- Lista de roles asignados.
- **Acción:** "Agregar nuevo rol" (abre selector para activar ventas, cobranza, etc.).
- Switch para activar/desactivar roles individualmente.

### C. Perfiles Específicos (Dynamic Content)
- **Si es Vendedor:** Nivel actual, histórico de ventas, tasa de comisión asignada.
- **Si es Cobrador:** Meta quincenal, zona asignada.
- **Si es Ajustador:** Número de cédula, vehículos asignados.

## 4. Próximos Pasos (Hoy)
1. **Frontend:** Crear el archivo base `index.tsx` para la lista.
2. **Backend:** Endpoint `GET /api/v1/employees` que traiga la información unificada con sus roles.
3. **Pincelazo:** Diseñar la card de empleado para que se sienta moderna y limpia.

---
*Propuesto por Claudy — ¿Le damos al primer pincelazo del frontend, Fer?*
