# UI Standards — Cobranza-rt Mobile

> **Regla de oro:** Antes de diseñar una pantalla nueva, leer este archivo.
> Antes de crear un componente nuevo, verificar que no exista ya uno con el patrón correcto.
> Decisiones tomadas en conjunto Fer + Claudy. No cambiar sin discutirlo primero.

---

## 🗂️ Índice
1. [Headers](#1-headers)
2. [Filter Chips](#2-filter-chips)
3. [Botones de acción](#3-botones-de-acción)
4. [Field Labels](#4-field-labels)
5. [Date Section](#5-date-section)
6. [Cards](#6-cards)
7. [Colores semánticos](#7-colores-semánticos)
8. [Flujo de trabajo UI/UX](#8-flujo-de-trabajo-uiux)

---

## 1. Headers

### Pantalla con navegación (back button)
Todas las pantallas navegadas usan este patrón exacto:

```tsx
<View style={styles.header}>
  <Pressable onPress={() => router.back()} style={{ width: 40 }}>
    <Ionicons name="chevron-back" size={24} color={colors.white} />
  </Pressable>
  <Text style={styles.headerTitle}>Título de la Pantalla</Text>
  <View style={{ width: 40 }} />   {/* spacer para centrar el título */}
</View>
```

**Con acción en la derecha** (ej. notificaciones con ⚙):
```tsx
<View style={styles.header}>
  <Pressable onPress={() => router.back()} style={{ width: 40 }}>
    <Ionicons name="chevron-back" size={24} color={colors.white} />
  </Pressable>
  <Text style={styles.headerTitle}>Título</Text>
  <Pressable style={{ width: 40, alignItems: 'flex-end' }}>
    <Ionicons name="settings-outline" size={22} color={colors.white} />
  </Pressable>
</View>
```

**Con subtítulo** (folio + cliente — ej. cobros, avisos):
```tsx
<View style={styles.header}>
  <Pressable onPress={() => router.back()} style={{ width: 40 }}>
    <Ionicons name="chevron-back" size={24} color={colors.white} />
  </Pressable>
  <View style={{ flex: 1 }}>
    <Text style={styles.headerTitle}>Título Principal</Text>
    <Text style={styles.headerSub}>F: 18405 · María López</Text>
  </View>
</View>
```
> ⚠️ Pantallas con subtítulo NO llevan el título centrado — el bloque completo va a la izquierda.

### Estilos base del header
```ts
header: {
  flexDirection: 'row',
  alignItems: 'center',
  paddingHorizontal: 16,
  paddingVertical: 12,
  backgroundColor: colors.primary,
},
headerTitle: {
  fontSize: 20,
  fontWeight: '700',
  color: colors.white,
  flex: 1,
  textAlign: 'center',   // ← OBLIGATORIO en pantallas sin subtítulo
},
headerSub: {
  fontSize: 14,
  color: 'rgba(255,255,255,0.85)',
  marginTop: 2,
},
```

### Pantalla raíz de tab (sin back, con acciones)
```tsx
<View style={styles.header}>
  <Pressable style={{ width: 40 }}>
    <Ionicons name="menu" size={22} color={colors.textDark} />
  </Pressable>
  <Text style={styles.headerTitle}>Proteg-rt</Text>
  <Pressable style={{ width: 40, alignItems: 'flex-end' }}>
    <Ionicons name="notifications" size={24} color={colors.textDark} />
  </Pressable>
</View>
```

---

## 2. Filter Chips

Estilo unificado para **todas** las pantallas con filtros:

```tsx
<View style={styles.filters}>
  {FILTERS.map(f => (
    <Pressable
      key={f.key}
      style={[styles.chip, filter === f.key && styles.chipActive]}
      onPress={() => setFilter(f.key)}
    >
      <Text style={[styles.chipText, filter === f.key && styles.chipTextActive]}>
        {f.label}
      </Text>
    </Pressable>
  ))}
</View>
```

```ts
filters: {
  flexDirection: 'row',
  gap: 8,
  paddingHorizontal: 20,
  paddingVertical: 12,
},
chip: {
  paddingHorizontal: 16,
  paddingVertical: 8,
  borderRadius: radius.full,
  backgroundColor: colors.white,
  borderWidth: 1,
  borderColor: colors.border,
},
chipActive: {
  backgroundColor: colors.primary,   // ← SIEMPRE morado, nunca negro
  borderColor: colors.primary,
},
chipText: {
  fontSize: 13,
  fontWeight: '600',
  color: colors.textMedium,
},
chipTextActive: {
  color: colors.white,
  fontWeight: '700',
},
```

> ⚠️ El chip activo es **siempre morado** (`colors.primary`). Nunca negro, nunca gris.
> Para listas largas (más de 4 filtros): usar `ScrollView horizontal`.

---

## 3. Botones de acción

### Jerarquía de botones en una misma pantalla
1. **Primario** — acción principal, fondo sólido
2. **Secundario** — acción alternativa, outline con borde
3. **Terciario** — acción de menor peso, outline gris sutil

```ts
// Primario (ej. COBRO COMPLETO)
btnPrimary: {
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: colors.success,   // verde para cobro completo
  borderRadius: 14,
  paddingVertical: 16,
},

// Primario variante — acción de envío (ej. ENVIAR PROPUESTA)
btnSubmit: {
  backgroundColor: colors.primary,   // morado para envíos generales
  borderRadius: 14,
  paddingVertical: 16,
},

// Secundario (ej. ABONO PARCIAL)
btnSecondary: {
  backgroundColor: colors.white,
  borderRadius: 14,
  paddingVertical: 16,
  borderWidth: 2,
  borderColor: colors.primary,
},

// Terciario (ej. AVISO DE VISITA)
btnTertiary: {
  backgroundColor: colors.white,
  borderRadius: 14,
  paddingVertical: 14,
  borderWidth: 1.5,
  borderColor: '#D0D0DC',   // gris suave, no compite con los anteriores
},
```

### Semántica de color en botones de cobro
| Acción | Color | Razón |
|---|---|---|
| Cobro completo | `colors.success` (verde) | Pago finalizado ✅ |
| Abono parcial | `colors.primary` (morado) | Acción de la app 💜 |
| Aviso de visita | Gris outline | Acción informativa, menor peso |

---

## 4. Field Labels

Todas las etiquetas de campos en formularios van en **ALL CAPS**:

```ts
fieldLabel: {
  fontSize: 12,
  fontWeight: '700',
  color: '#555',
  letterSpacing: 0.5,
  marginBottom: 8,
  marginTop: 4,
},
```

> ✅ Correcto: `MONTO COBRADO`, `MÉTODO DE PAGO`, `NÚMERO DE RECIBO`
> ❌ Incorrecto: `Monto cobrado`, `Método de pago`, `Número de recibo`

---

## 5. Date Section

Encabezado contextual de pantallas tipo lista. Se usa debajo del header principal:

```tsx
<View style={styles.dateSection}>
  <Text style={styles.dateTitle}>{formatDateFull(new Date().toISOString())}</Text>
  <Text style={styles.dateSubtitle}>4 folios asignados</Text>
</View>
```

```ts
dateSection: {
  backgroundColor: colors.white,
  paddingHorizontal: 20,
  paddingVertical: 16,
},
dateTitle: {
  fontSize: 22,
  fontWeight: '700',
  color: '#1C1C1E',
},
dateSubtitle: {
  fontSize: 13,
  color: colors.primary,
  marginTop: 2,
},
```

> Usado en: `folios/index.tsx`, `propuestas.tsx`

---

## 6. Cards

### Card base con borde izquierdo de color (estado del folio)
```tsx
<Card
  leftBorderColor={borderColors[item.overdue_level]}
  onPress={() => router.push(`/(cobrador)/folios/${item.folio}`)}
>
  {/* contenido */}
</Card>
```

### Card de propuesta / cobro (borde izquierdo semántico)
```ts
proposalCard: {
  backgroundColor: colors.white,
  borderRadius: 12,
  padding: 16,
  marginHorizontal: 16,
  marginBottom: 12,
  borderLeftWidth: 4,
  borderLeftColor: cfg.border,   // verde/amarillo/rojo según estatus
  shadowColor: '#000',
  shadowOffset: { width: 0, height: 1 },
  shadowOpacity: 0.06,
  shadowRadius: 4,
  elevation: 1,
},
```

### Card de Estado de Cuenta (en pantalla de cobro)
```ts
accountCard: {
  backgroundColor: colors.white,
  borderRadius: 12,
  padding: 20,
  marginBottom: 24,
  shadowColor: '#000',
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.06,
  shadowRadius: 8,
  elevation: 2,
},
```

---

## 7. Colores semánticos

| Concepto | Color | Uso |
|---|---|---|
| Primario / brand | `colors.primary` (#4A3AFF / morado) | Chips activos, acciones principales |
| Éxito / completo | `colors.success` (#34C759 / verde) | Cobro completo, aprobado |
| Advertencia | `#F5A623` / `#FEF3C7` | Pendiente, abono parcial |
| Error / vencido | `colors.error` (#FF3B30 / rojo) | Rechazado, muy atrasado |
| Progress bar completo | `#34C759` (verde) | Progreso por número de pagos |
| Progress bar parcial | `colors.primary` (morado) | Progreso por monto abonado |

> Los colores de progress bar son **intencionales y distintos** — verde = pagos completados, morado = monto parcial abonado. No es inconsistencia, es semántica visual.

---

## 8. Flujo de trabajo UI/UX

> Ver también: `SISTEMA-NUEVO-GAPS.md` → sección "Principio de Trabajo"

**Discutir → Acordar → Ejecutar.** Sin excepción.

1. Claudy señala inconsistencia o propone componente
2. Fer da contexto de negocio si aplica y opina
3. Se acuerda la solución **antes** de tocar código
4. Claudy ejecuta el cambio acordado y actualiza este archivo

Cuando se diseñe una pantalla nueva:
- [ ] Revisar este archivo antes de empezar
- [ ] Reutilizar patrones existentes
- [ ] Si se necesita algo nuevo → discutirlo y documentarlo aquí antes de implementar

---

_Última actualización: 2026-02-25 — Fer + Claudy_
