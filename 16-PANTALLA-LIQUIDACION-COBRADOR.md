# 16 - Liquidación de Cobradores ✨

**Fecha:** 2026-02-26
**Diseño:** Claudy 💜
**Validación:** Fer
**Estado:** En diseño creativo 🎨

---

## LA VISIÓN

Elena abre la app. Ve a sus 6 cobradores como cartas.
Cada carta le dice en UN VISTAZO: cuánto le toca, si hay algún problema, si ya le pagó.
Toca una carta. Ve el desglose. Un botón grande dice "Pagar $1,245".
Lo presiona. Animación satisfactoria. Listo. Siguiente.

**En 5 minutos liquidó a todos.** No abrió Excel. No calculó nada. No se equivocó.

---

## PANTALLA 1: Vista General de Liquidaciones

**Ruta:** `/gerente/liquidaciones`

### Concepto
Una vista de cartas (no una tabla) donde cada cobrador es una "tarjeta de liquidación".
Elena ve TODO de un vistazo sin tener que entrar a cada uno.

```
╔══════════════════════════════════════════════════════════╗
║  ←  Liquidaciones                              [⚙️]     ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║   ┌─────────────────────────────────────────────────┐   ║
║   │  📅  2da Quincena · Febrero 2026         [▼]   │   ║
║   └─────────────────────────────────────────────────┘   ║
║                                                          ║
║   6 cobradores · 3 listos · 2 con alertas · 1 pagado    ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║   ┌────────────────────────────────────────────────┐    ║
║   │                                                │    ║
║   │  [EM]  Edgar Martínez                    ✓    │    ║
║   │        ━━━━━━━━━━━━━━━━━━━━━━░░░░ 78%         │    ║
║   │                                                │    ║
║   │   💰 $1,995    📉 -$600    ═══    $1,395     │    ║
║   │   comisiones    deduc.           NETO        │    ║
║   │                                                │    ║
║   │   🟢 Listo para pagar                         │    ║
║   │                                                │    ║
║   └────────────────────────────────────────────────┘    ║
║                                                          ║
║   ┌────────────────────────────────────────────────┐    ║
║   │                                                │    ║
║   │  [LJ]  Laura Jiménez                     🏆   │    ║
║   │        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 112%      │    ║
║   │                                                │    ║
║   │   💰 $2,340    📉 -$450    ═══    $1,890     │    ║
║   │                                                │    ║
║   │   🟢 Listo para pagar · ¡Superó su meta!      │    ║
║   │                                                │    ║
║   └────────────────────────────────────────────────┘    ║
║                                                          ║
║   ┌────────────────────────────────────────────────┐    ║
║   │                                                │    ║
║   │  [CV]  Carlos Vega                       ⚠️   │    ║
║   │        ━━━━━━━━━━━━━━░░░░░░░░░░░░ 52%         │    ║
║   │                                                │    ║
║   │   💰 $900     📉 -$1,050   ═══    -$150      │    ║
║   │                                                │    ║
║   │   🟡 Saldo negativo — revisar deducciones     │    ║
║   │                                                │    ║
║   └────────────────────────────────────────────────┘    ║
║                                                          ║
║   ┌────────────────────────────────────────────────┐    ║
║   │                                                │    ║
║   │  [MR]  Miguel Ruiz                       ✓    │    ║
║   │                                                │    ║
║   │   ✅ Pagado el 28 feb · $1,120                │    ║
║   │                                                │    ║
║   └────────────────────────────────────────────────┘    ║
║                                                          ║
║   ─────────────────────────────────────────────────     ║
║                                                          ║
║   ┌────────────────────────────────────────────────┐    ║
║   │     💳  PAGAR TODOS LOS LISTOS  (3)           │    ║ ← Batch action
║   │              $4,530.00                         │    ║
║   └────────────────────────────────────────────────┘    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

### Elementos de cada carta

**Indicadores visuales:**
- ✓ = Listo para pagar (sin problemas)
- 🏆 = Superó su meta (celebrar el logro)
- ⚠️ = Tiene alertas (saldo negativo, diferencias pendientes)
- ✅ = Ya pagado este período

**Barra de progreso:**
- Muestra % de meta alcanzada
- Verde si pasó del 100%, amarillo si está bajo

**Resumen en 3 números:**
- Comisiones ganadas
- Deducciones
- **NETO** (destacado, es lo que importa)

**Status contextual:**
- "Listo para pagar"
- "¡Superó su meta!"
- "Saldo negativo — revisar deducciones"
- "Falta justificar $150 de diferencia"
- "Pagado el [fecha]"

### Interacciones

| Gesto | Acción |
|-------|--------|
| Tap en carta | Abre detalle de liquidación |
| Swipe izquierda | Acción rápida: "Pagar" (si está listo) |
| Botón "Pagar todos" | Liquida todos los que están en verde |
| Pull to refresh | Recalcula con datos más recientes |

---

## PANTALLA 2: Detalle de Liquidación

**Ruta:** `/gerente/liquidaciones/[cobrador_id]`

Al tocar una carta, se abre el detalle con una transición suave (la carta se "expande").

```
╔══════════════════════════════════════════════════════════╗
║  ←  Edgar Martínez                           [...]      ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║   ┌────────────────────────────────────────────────┐    ║
║   │                                                │    ║
║   │              [EM]                              │    ║
║   │         Edgar Martínez                         │    ║
║   │      Cobrador · Nivel 1 · 2 años              │    ║
║   │                                                │    ║
║   │      ━━━━━━━━━━━━━━━━━━━━━━░░░░ 78%           │    ║
║   │      $13,200 de $17,000 meta                  │    ║
║   │                                                │    ║
║   └────────────────────────────────────────────────┘    ║
║                                                          ║
║   ┌────────────────────────────────────────────────┐    ║
║   │                                                │    ║
║   │          $1,395.00                            │    ║
║   │          NETO A PAGAR                          │    ║
║   │                                                │    ║
║   │   ┌──────────────────────────────────────┐    │    ║
║   │   │      💳  PAGAR AHORA                 │    │    ║
║   │   └──────────────────────────────────────┘    │    ║
║   │                                                │    ║
║   └────────────────────────────────────────────────┘    ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║   💰 COMISIONES                           +$1,995.00    ║
║   ┌────────────────────────────────────────────────┐    ║
║   │                                                │    ║
║   │  Cobranza normal (10%)                        │    ║
║   │  12 cobros · $13,200                 +$1,320  │    ║
║   │  ─────────────────────────────────────────    │    ║
║   │  Pagos de contado (5%)                        │    ║
║   │  3 cobros · $8,500                     +$425  │    ║
║   │  ─────────────────────────────────────────    │    ║
║   │  Entregas ($50 c/u)                           │    ║
║   │  5 pólizas/endosos                     +$250  │    ║
║   │                                                │    ║
║   │  [Ver 15 cobros del período →]                │    ║
║   │                                                │    ║
║   └────────────────────────────────────────────────┘    ║
║                                                          ║
║   📉 DEDUCCIONES                           -$600.00     ║
║   ┌────────────────────────────────────────────────┐    ║
║   │                                                │    ║
║   │  ⛽ Gasolina (50%)                             │    ║
║   │  6 cargas · $800 total                  -$400  │    ║
║   │  ─────────────────────────────────────────    │    ║
║   │  🏍️ Préstamo moto                             │    ║
║   │  Cuota 4 de 12                          -$200  │    ║
║   │  ─────────────────────────────────────────    │    ║
║   │  ⚠️ Diferencias                          $0   │    ║
║   │  Sin diferencias este período ✓               │    ║
║   │                                                │    ║
║   │  [+ Agregar deducción manual]                 │    ║
║   │                                                │    ║
║   └────────────────────────────────────────────────┘    ║
║                                                          ║
║   📜 HISTORIAL                                          ║
║   ┌────────────────────────────────────────────────┐    ║
║   │  1ra Qna Feb 2026    $1,180    ✅ Pagado      │    ║
║   │  2da Qna Ene 2026    $1,450    ✅ Pagado      │    ║
║   │  1ra Qna Ene 2026    $980      ✅ Pagado      │    ║
║   │  [Ver más →]                                   │    ║
║   └────────────────────────────────────────────────┘    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

### Secciones colapsables

Por default:
- **Header + Neto + Botón:** Siempre visible (lo más importante arriba)
- **Comisiones:** Expandido (Elena quiere ver el desglose)
- **Deducciones:** Expandido
- **Historial:** Colapsado (solo si quiere verificar)

Cada sección se puede colapsar/expandir tocando el header.

---

## PANTALLA 3: Confirmación de Pago

Al presionar "PAGAR AHORA", NO es un simple alert. Es un momento.

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║                                                          ║
║                                                          ║
║                       [EM]                               ║
║                  Edgar Martínez                          ║
║                                                          ║
║                                                          ║
║                    $1,395.00                             ║
║                                                          ║
║              2da Quincena · Feb 2026                     ║
║                                                          ║
║                                                          ║
║         ┌────────────────────────────────┐              ║
║         │  💵  Efectivo                  │              ║
║         └────────────────────────────────┘              ║
║         ┌────────────────────────────────┐              ║
║         │  📱  Transferencia             │              ║
║         └────────────────────────────────┘              ║
║                                                          ║
║                                                          ║
║         ┌────────────────────────────────┐              ║
║         │                                │              ║
║         │    ✓  CONFIRMAR PAGO           │              ║
║         │                                │              ║
║         └────────────────────────────────┘              ║
║                                                          ║
║                    [Cancelar]                            ║
║                                                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

### Al confirmar

1. **Animación de éxito** — checkmark que se dibuja, confetti sutil, algo que se sienta bien
2. **Feedback háptico** — vibración suave de confirmación
3. **Sonido opcional** — un "ding" satisfactorio
4. **Regresa a la lista** — la carta ahora muestra "✅ Pagado"

---

## DETALLES QUE HACEN LA DIFERENCIA

### 1. Período inteligente
- Al abrir, auto-selecciona el período actual
- Si estamos entre el 1-3 del mes, sugiere "¿Liquidar la 2da quincena del mes anterior?"

### 2. Celebrar los logros
- Cobrador que superó su meta → 🏆 y mensaje de felicitación
- Primer lugar del período → badge especial
- Racha de quincenas cumpliendo meta → streak counter

### 3. Alertas accionables
No solo "hay un problema", sino "hay un problema Y aquí está cómo resolverlo":
- "Saldo negativo" → botón "Ajustar deducciones"
- "Diferencia sin justificar" → botón "Ver entrega del 22 feb"
- "Faltan cargas de gasolina" → botón "Importar período"

### 4. Pago en lote
El botón "Pagar todos los listos" es poderoso:
- Muestra cuántos y el total
- Confirmación grupal con lista de nombres
- Genera un solo registro de "liquidación masiva"
- Opción de generar reporte PDF de todo el lote

### 5. Sin fricción innecesaria
- No pedir confirmación doble para montos pequeños
- Recordar el método de pago preferido de cada cobrador
- Auto-guardar notas como draft mientras escribe

---

## ANIMACIONES Y TRANSICIONES

| Momento | Animación |
|---------|-----------|
| Abrir detalle | Carta se expande (shared element transition) |
| Cerrar detalle | Carta se contrae de vuelta |
| Marcar como pagado | Checkmark se dibuja + carta cambia a estado "pagado" |
| Pago en lote | Cartas se "apilan" y luego aparece confetti |
| Pull to refresh | Bounce elástico + shimmer en datos |
| Alerta nueva | Carta hace "shake" sutil |

---

## ¿POR QUÉ ESTE DISEÑO?

1. **Vista general primero** — Elena no tiene que entrar a cada cobrador para saber cómo están
2. **Acción donde está la información** — El botón de pagar está JUNTO al monto, no en otro lado
3. **Problemas visibles** — Las alertas no se esconden, están en la carta
4. **Satisfacción** — Liquidar se siente como completar algo, no como llenar un formulario
5. **Respeta su tiempo** — Con "Pagar todos" puede terminar en segundos

---

## LO QUE LEGACY NUNCA TUVO

| Legacy | Nuestro Sistema |
|--------|-----------------|
| Tabla con datos | Cartas con contexto visual |
| Exportar a Excel para calcular | Cálculo automático en pantalla |
| Sin indicadores de status | Estados claros con colores |
| Una persona a la vez | Vista de todos + pago en lote |
| Sin historial integrado | Historial en la misma pantalla |
| Sin celebraciones | Reconocimiento de logros |
| Proceso tedioso | Proceso satisfactorio |

---

## MODELO DE DATOS

*(Se mantiene el modelo propuesto anteriormente — la magia está en la UI, no en cambiar la estructura de datos)*

---

## SIGUIENTE PASO

Implementar `LiquidacionesScreen.tsx` con:
1. Vista de cartas (FlatList con cards)
2. Cálculo de comisiones/deducciones en tiempo real
3. Transición a detalle
4. Flujo de confirmación de pago
5. Animaciones que se sientan bien

---

*Diseñado con amor por Claudy ✨ para que Elena nunca más tenga que abrir Excel para esto.*
