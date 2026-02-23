/**
 * Paleta extraída de los mockups de Stitch — aprobados por Óscar y Elena.
 * NO CAMBIAR sin autorización de Fer.
 */
export const colors = {
  // ── Brand (Stitch mockup) ────────────
  primary: '#4A3AFF',
  primaryLight: '#6C5CE7',
  primaryBg: '#EDE9FF',

  // ── Text ─────────────────────────────
  textDark: '#1A1A2E',
  textMedium: '#8E8E9A',
  textLight: '#B0B0BE',

  // ── Semantic ─────────────────────────
  success: '#4CAF50',
  successBg: '#E8F5E9',
  error: '#FF3B30',
  errorBg: '#FFEBEE',
  orange: '#FF6B35',
  orangeBg: '#FFF0E6',
  badgeRed: '#FF3B30',

  // ── Atraso de pago (bordes cards) ────
  overdueHigh: '#FF3B30',    // >15 días
  overdueMid: '#FF6B35',     // 5-15 días
  overdueLow: '#EAB308',     // 1-5 días
  onTime: '#4CAF50',         // Al día
  collected: '#B0B0BE',      // Ya cobrado

  // ── Surfaces ─────────────────────────
  white: '#FFFFFF',
  background: '#F8F8FC',
  border: '#F0F0F5',
  divider: '#F5F5FA',

  // ── Overlay ──────────────────────────
  overlay: 'rgba(0, 0, 0, 0.5)',
} as const;

export type ColorKey = keyof typeof colors;
