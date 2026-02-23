export const colors = {
  // ── Brand ────────────────────────────
  primary: '#4F46E5',       // Indigo — botones principales
  primaryLight: '#6366F1',
  primaryDark: '#4338CA',

  // ── Semantic ─────────────────────────
  success: '#16A34A',       // Verde — aprobado
  successLight: '#DCFCE7',
  warning: '#D97706',       // Amarillo — pendiente
  warningLight: '#FEF3C7',
  danger: '#DC2626',        // Rojo — rechazado / error
  dangerLight: '#FEE2E2',
  dangerDark: '#991B1B',    // Rojo oscuro — atraso >15 días

  // ── Atraso de pago ───────────────────
  overdueHigh: '#991B1B',   // >15 días — rojo oscuro
  overdueMid: '#DC2626',    // 5-15 días — naranja/rojo
  overdueLow: '#D97706',    // 1-5 días — amarillo
  onTime: '#16A34A',        // Al día — verde
  collected: '#6B7280',     // Ya cobrado — gris

  // ── Neutrals ─────────────────────────
  white: '#FFFFFF',
  gray50: '#F9FAFB',
  gray100: '#F3F4F6',
  gray200: '#E5E7EB',
  gray300: '#D1D5DB',
  gray400: '#9CA3AF',
  gray500: '#6B7280',
  gray600: '#4B5563',
  gray700: '#374151',
  gray800: '#1F2937',
  gray900: '#111827',
  black: '#000000',

  // ── Backgrounds ──────────────────────
  background: '#F0F2F5',
  surface: '#FFFFFF',
  overlay: 'rgba(0, 0, 0, 0.5)',
} as const;

export type ColorKey = keyof typeof colors;
