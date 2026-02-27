/**
 * Detalle de Liquidación - Vista individual de un cobrador
 *
 * Diseño: Claudy ✨
 * Desglose completo + botón de pago que se siente bien.
 * Conectado a la API real el 2026-02-27.
 *
 * El parámetro `id` de la URL es employee_role_id.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  Modal,
  ActivityIndicator,
  TextInput,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { colors, spacing, radius, cardShadow } from '@/theme';
import { formatMoney } from '@/utils/format';
import {
  getPreview,
  getSettlementHistory,
  createSettlement,
  toApiMethod,
  type SettlementPreview,
  type SettlementHistoryItem,
} from '@/api/settlements';

// ─── Period helpers ───────────────────────────────────────────────────────────

const MONTHS_ES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
];

function getCurrentPeriodDates(): { start: string; end: string; label: string } {
  const now = new Date();
  const day = now.getDate();
  const month = now.getMonth() + 1;
  const year = now.getFullYear();
  const mm = String(month).padStart(2, '0');

  if (day <= 5) {
    const lastMonthDate = new Date(year, month - 2, 1);
    const lm = lastMonthDate.getMonth() + 1;
    const ly = lastMonthDate.getFullYear();
    const lmm = String(lm).padStart(2, '0');
    const lastDay = new Date(ly, lm, 0).getDate();
    return {
      start: `${ly}-${lmm}-16`,
      end: `${ly}-${lmm}-${lastDay}`,
      label: `2da Quincena · ${MONTHS_ES[lm - 1]} ${ly}`,
    };
  }

  if (day <= 20) {
    return {
      start: `${year}-${mm}-01`,
      end: `${year}-${mm}-15`,
      label: `1ra Quincena · ${MONTHS_ES[month - 1]} ${year}`,
    };
  } else {
    const lastDay = new Date(year, month, 0).getDate();
    return {
      start: `${year}-${mm}-16`,
      end: `${year}-${mm}-${lastDay}`,
      label: `2da Quincena · ${MONTHS_ES[month - 1]} ${year}`,
    };
  }
}

// ─── Types ────────────────────────────────────────────────────────────────────

interface DeduccionDetalle {
  id: string;
  concepto: string;
  descripcion: string;
  monto: number;
  tipo: 'gasolina' | 'prestamo' | 'diferencia';
}

// ─── Components ───────────────────────────────────────────────────────────────

function Section({
  title,
  total,
  totalColor = colors.textDark,
  icon,
  children,
  defaultExpanded = true,
}: {
  title: string;
  total?: number;
  totalColor?: string;
  icon?: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
}) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  return (
    <View style={styles.section}>
      <Pressable style={styles.sectionHeader} onPress={() => setExpanded(!expanded)}>
        <View style={styles.sectionTitleRow}>
          {icon && <Text style={styles.sectionIcon}>{icon}</Text>}
          <Text style={styles.sectionTitle}>{title}</Text>
        </View>
        <View style={styles.sectionRight}>
          {total !== undefined && (
            <Text style={[styles.sectionTotal, { color: totalColor }]}>
              {total >= 0 ? '+' : ''}{formatMoney(total)}
            </Text>
          )}
          <Ionicons
            name={expanded ? 'chevron-up' : 'chevron-down'}
            size={18}
            color={colors.textMedium}
          />
        </View>
      </Pressable>

      {expanded && <View style={styles.sectionContent}>{children}</View>}
    </View>
  );
}

function ComisionRow({
  label,
  detail,
  amount,
  isLast = false,
}: {
  label: string;
  detail: string;
  amount: number;
  isLast?: boolean;
}) {
  return (
    <View style={[styles.comisionRow, !isLast && styles.comisionRowBorder]}>
      <View style={styles.comisionInfo}>
        <Text style={styles.comisionLabel}>{label}</Text>
        <Text style={styles.comisionDetail}>{detail}</Text>
      </View>
      <Text style={styles.comisionAmount}>+{formatMoney(amount)}</Text>
    </View>
  );
}

function DeduccionRow({
  item,
  isLast = false,
}: {
  item: DeduccionDetalle;
  isLast?: boolean;
}) {
  const iconMap = {
    gasolina: '⛽',
    prestamo: '🏍️',
    diferencia: '⚠️',
  };

  return (
    <View style={[styles.comisionRow, !isLast && styles.comisionRowBorder]}>
      <View style={styles.comisionInfo}>
        <Text style={styles.comisionLabel}>
          {iconMap[item.tipo]} {item.concepto}
        </Text>
        <Text style={styles.comisionDetail}>{item.descripcion}</Text>
      </View>
      <Text style={[styles.comisionAmount, styles.deduccionAmount]}>
        -{formatMoney(item.monto)}
      </Text>
    </View>
  );
}

// ─── Payment Modal ────────────────────────────────────────────────────────────

function PaymentModal({
  visible,
  onClose,
  onConfirm,
  cobrador,
  neto,
  periodo,
}: {
  visible: boolean;
  onClose: () => void;
  onConfirm: (method: string) => Promise<void>;
  cobrador: { nombre: string; initials: string; avatarColor: string };
  neto: number;
  periodo: string;
}) {
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null);
  const [confirming, setConfirming] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleConfirm = async () => {
    if (!selectedMethod) return;
    setConfirming(true);
    setError(null);
    try {
      await onConfirm(selectedMethod);
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        setConfirming(false);
        setSelectedMethod(null);
      }, 1500);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Error al registrar el pago');
      setConfirming(false);
    }
  };

  const handleClose = () => {
    setSelectedMethod(null);
    setSuccess(false);
    setConfirming(false);
    setError(null);
    onClose();
  };

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={handleClose}>
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          {success ? (
            <View style={styles.successContainer}>
              <View style={styles.successIcon}>
                <Ionicons name="checkmark" size={48} color={colors.white} />
              </View>
              <Text style={styles.successTitle}>¡Pago Exitoso! ✨</Text>
              <Text style={styles.successSubtitle}>
                {cobrador.nombre} ha sido liquidado con éxito.
              </Text>
              <Text style={{ fontSize: 12, color: colors.primary, marginTop: 10, fontStyle: 'italic' }}>
                Tu gestión hace la diferencia. 💜
              </Text>
            </View>
          ) : (
            <>
              <View style={[styles.modalAvatar, { backgroundColor: cobrador.avatarColor }]}>
                <Text style={styles.modalAvatarText}>{cobrador.initials}</Text>
              </View>

              <Text style={styles.modalName}>{cobrador.nombre}</Text>
              <Text style={styles.modalAmount}>{formatMoney(neto)}</Text>
              <Text style={styles.modalPeriodo}>{periodo}</Text>

              {error && (
                <Text style={styles.modalError}>{error}</Text>
              )}

              <View style={styles.methodsContainer}>
                <Pressable
                  style={[
                    styles.methodButton,
                    selectedMethod === 'efectivo' && styles.methodSelected,
                  ]}
                  onPress={() => setSelectedMethod('efectivo')}
                >
                  <Ionicons
                    name="cash-outline"
                    size={24}
                    color={selectedMethod === 'efectivo' ? colors.primary : colors.textMedium}
                  />
                  <Text
                    style={[
                      styles.methodText,
                      selectedMethod === 'efectivo' && styles.methodTextSelected,
                    ]}
                  >
                    Efectivo
                  </Text>
                </Pressable>

                <Pressable
                  style={[
                    styles.methodButton,
                    selectedMethod === 'transferencia' && styles.methodSelected,
                  ]}
                  onPress={() => setSelectedMethod('transferencia')}
                >
                  <Ionicons
                    name="phone-portrait-outline"
                    size={24}
                    color={
                      selectedMethod === 'transferencia' ? colors.primary : colors.textMedium
                    }
                  />
                  <Text
                    style={[
                      styles.methodText,
                      selectedMethod === 'transferencia' && styles.methodTextSelected,
                    ]}
                  >
                    Transferencia
                  </Text>
                </Pressable>
              </View>

              <Pressable
                style={[
                  styles.confirmButton,
                  !selectedMethod && styles.confirmButtonDisabled,
                ]}
                onPress={handleConfirm}
                disabled={!selectedMethod || confirming}
              >
                {confirming ? (
                  <ActivityIndicator size="small" color={colors.white} />
                ) : (
                  <>
                    <Ionicons name="checkmark-circle" size={20} color={colors.white} />
                    <Text style={styles.confirmButtonText}>CONFIRMAR PAGO</Text>
                  </>
                )}
              </Pressable>

              <Pressable style={styles.cancelButton} onPress={handleClose}>
                <Text style={styles.cancelButtonText}>Cancelar</Text>
              </Pressable>
            </>
          )}
        </View>
      </View>
    </Modal>
  );
}

// ─── Add Deduccion Modal ──────────────────────────────────────────────────────

function AddDeduccionModal({
  visible,
  onClose,
  onAdd,
  cobradorNombre,
}: {
  visible: boolean;
  onClose: () => void;
  onAdd: (concepto: string, monto: number) => void;
  cobradorNombre: string;
}) {
  const [concepto, setConcepto] = useState('');
  const [monto, setMonto] = useState('');
  const [tipoSeleccionado, setTipoSeleccionado] = useState<string | null>(null);

  const tiposComunes = [
    { id: 'adelanto', label: 'Adelanto de sueldo', icon: '💵' },
    { id: 'prestamo', label: 'Préstamo personal', icon: '🏦' },
    { id: 'faltante', label: 'Faltante de efectivo', icon: '⚠️' },
    { id: 'otro', label: 'Otro', icon: '📝' },
  ];

  const handleAdd = () => {
    const montoNum = parseFloat(monto.replace(/,/g, ''));
    if (!concepto.trim() || isNaN(montoNum) || montoNum <= 0) return;
    onAdd(concepto.trim(), montoNum);
    setConcepto('');
    setMonto('');
    setTipoSeleccionado(null);
  };

  const handleTipoPress = (tipo: { id: string; label: string }) => {
    setTipoSeleccionado(tipo.id);
    if (tipo.id !== 'otro') {
      setConcepto(tipo.label);
    } else {
      setConcepto('');
    }
  };

  const handleClose = () => {
    setConcepto('');
    setMonto('');
    setTipoSeleccionado(null);
    onClose();
  };

  const isValid = concepto.trim() && monto && parseFloat(monto.replace(/,/g, '')) > 0;

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={handleClose}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={addModalStyles.overlay}
      >
        <View style={addModalStyles.content}>
          <View style={addModalStyles.header}>
            <Ionicons name="remove-circle-outline" size={28} color={colors.error} />
            <Text style={addModalStyles.title}>Agregar deducción</Text>
            <Text style={addModalStyles.subtitle}>Para {cobradorNombre}</Text>
          </View>

          <Text style={addModalStyles.label}>TIPO DE DEDUCCIÓN</Text>
          <View style={addModalStyles.tiposGrid}>
            {tiposComunes.map((tipo) => (
              <Pressable
                key={tipo.id}
                style={[
                  addModalStyles.tipoButton,
                  tipoSeleccionado === tipo.id && addModalStyles.tipoSelected,
                ]}
                onPress={() => handleTipoPress(tipo)}
              >
                <Text style={addModalStyles.tipoIcon}>{tipo.icon}</Text>
                <Text
                  style={[
                    addModalStyles.tipoLabel,
                    tipoSeleccionado === tipo.id && addModalStyles.tipoLabelSelected,
                  ]}
                >
                  {tipo.label}
                </Text>
              </Pressable>
            ))}
          </View>

          {tipoSeleccionado === 'otro' && (
            <>
              <Text style={addModalStyles.label}>CONCEPTO</Text>
              <TextInput
                style={addModalStyles.input}
                placeholder="Ej: Uniforme, herramienta..."
                placeholderTextColor={colors.textMedium}
                value={concepto}
                onChangeText={setConcepto}
              />
            </>
          )}

          <Text style={addModalStyles.label}>MONTO</Text>
          <View style={addModalStyles.montoContainer}>
            <Text style={addModalStyles.montoPrefix}>$</Text>
            <TextInput
              style={addModalStyles.montoInput}
              placeholder="0.00"
              placeholderTextColor={colors.textMedium}
              keyboardType="decimal-pad"
              value={monto}
              onChangeText={setMonto}
            />
          </View>

          <Pressable
            style={[addModalStyles.addButton, !isValid && addModalStyles.addButtonDisabled]}
            onPress={handleAdd}
            disabled={!isValid}
          >
            <Ionicons name="add-circle" size={20} color={colors.white} />
            <Text style={addModalStyles.addButtonText}>AGREGAR DEDUCCIÓN</Text>
          </Pressable>

          <Pressable style={addModalStyles.cancelButton} onPress={handleClose}>
            <Text style={addModalStyles.cancelButtonText}>Cancelar</Text>
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const addModalStyles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  content: {
    backgroundColor: colors.white,
    borderRadius: radius.xl,
    padding: spacing['2xl'],
    width: '100%',
    maxWidth: 340,
  },
  header: {
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.textDark,
    marginTop: spacing.sm,
  },
  subtitle: {
    fontSize: 13,
    color: colors.textMedium,
  },
  label: {
    fontSize: 10,
    fontWeight: '700',
    color: colors.textMedium,
    letterSpacing: 0.5,
    marginBottom: spacing.sm,
    marginTop: spacing.md,
  },
  tiposGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  tipoButton: {
    width: '48%',
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: radius.md,
    borderWidth: 1.5,
    borderColor: colors.border,
    gap: spacing.sm,
  },
  tipoSelected: {
    borderColor: colors.primary,
    backgroundColor: colors.primaryBg,
  },
  tipoIcon: { fontSize: 16 },
  tipoLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: colors.textMedium,
    flex: 1,
  },
  tipoLabelSelected: {
    color: colors.primary,
    fontWeight: '600',
  },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    fontSize: 15,
    color: colors.textDark,
  },
  montoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
  },
  montoPrefix: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textMedium,
    marginRight: spacing.sm,
  },
  montoInput: {
    flex: 1,
    fontSize: 24,
    fontWeight: '700',
    color: colors.textDark,
    paddingVertical: spacing.md,
  },
  addButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.error,
    paddingVertical: spacing.lg,
    borderRadius: radius.md,
    marginTop: spacing.xl,
    gap: spacing.sm,
  },
  addButtonDisabled: { opacity: 0.5 },
  addButtonText: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.white,
  },
  cancelButton: {
    paddingVertical: spacing.md,
    alignItems: 'center',
    marginTop: spacing.sm,
  },
  cancelButtonText: {
    fontSize: 14,
    color: colors.textMedium,
    fontWeight: '500',
  },
});

// ─── Main Screen ──────────────────────────────────────────────────────────────

const AVATAR_COLORS = [
  '#6D28D9', '#D97706', '#4F46E5', '#059669',
  '#DC2626', '#2563EB', '#7C3AED', '#DB2777',
];

function getInitials(fullName: string): string {
  const parts = fullName.trim().split(' ');
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  return parts[0].slice(0, 2).toUpperCase();
}

function deductionTypeToTipo(type: string): DeduccionDetalle['tipo'] {
  if (type === 'fuel') return 'gasolina';
  if (type === 'loan') return 'prestamo';
  return 'diferencia';
}

export default function LiquidacionDetalleScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const employeeRoleId = parseInt(id, 10);

  const period = getCurrentPeriodDates();

  // ── State ──────────────────────────────────────────────────────────────────

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<SettlementPreview | null>(null);
  const [historial, setHistorial] = useState<SettlementHistoryItem[]>([]);
  const [deducciones, setDeducciones] = useState<DeduccionDetalle[]>([]);

  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showDeduccionModal, setShowDeduccionModal] = useState(false);
  const [paid, setPaid] = useState(false);

  // ── Fetch ──────────────────────────────────────────────────────────────────

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [previewData, historyData] = await Promise.all([
        getPreview(employeeRoleId, period.start, period.end),
        getSettlementHistory(employeeRoleId, 10),
      ]);

      setPreview(previewData);
      setHistorial(historyData.items);

      // Mapear deducciones del API a tipo local
      const deduccionesApi: DeduccionDetalle[] = previewData.deductions.items.map((d, i) => ({
        id: d.id ? String(d.id) : `api-${i}`,
        concepto: d.concept,
        descripcion: d.description || '',
        monto: Number(d.amount),
        tipo: deductionTypeToTipo(d.type),
      }));
      setDeducciones(deduccionesApi);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'No se pudo cargar la liquidación');
    } finally {
      setLoading(false);
    }
  }, [employeeRoleId, period.start, period.end]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // ── Derived ────────────────────────────────────────────────────────────────

  const totalDeducciones = deducciones.reduce((sum, d) => sum + d.monto, 0);
  const totalComisiones = preview ? Number(preview.commissions.total) : 0;
  const neto = totalComisiones - totalDeducciones;

  const cobrador = preview
    ? {
        nombre: preview.employee.full_name,
        initials: getInitials(preview.employee.full_name),
        avatarColor: AVATAR_COLORS[employeeRoleId % AVATAR_COLORS.length],
        nivel: 1,
        antiguedad: '',
        metaCobro: Number(preview.goal_amount),
        totalCobrado: Number(preview.total_collected),
        porcentajeMeta: Math.min(Math.round(preview.goal_percentage), 100),
      }
    : null;

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleAddDeduccion = (concepto: string, monto: number) => {
    const nuevaDeduccion: DeduccionDetalle = {
      id: `manual-${Date.now()}`,
      concepto,
      descripcion: 'Agregado manualmente',
      monto,
      tipo: 'diferencia',
    };
    setDeducciones((prev) => [...prev, nuevaDeduccion]);
    setShowDeduccionModal(false);
    // TODO: cuando haya settlement_id pendiente, llamar addManualDeduction()
  };

  const handlePaymentConfirm = async (method: string) => {
    if (!preview) return;
    await createSettlement({
      employee_role_id: employeeRoleId,
      period_start: period.start,
      period_end: period.end,
      payment_method: toApiMethod(method),
    });
    setPaid(true);
    // Cerrar modal + volver después del ícono de éxito
    setTimeout(() => {
      setShowPaymentModal(false);
      router.back();
    }, 1800);
  };

  // ── Loading / Error ────────────────────────────────────────────────────────

  if (loading) {
    return (
      <SafeAreaView edges={['top']} style={styles.safe}>
        <View style={styles.header}>
          <Pressable onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="chevron-back" size={24} color={colors.white} />
          </Pressable>
          <Text style={styles.headerTitle}>Liquidación</Text>
          <View style={{ width: 40 }} />
        </View>
        <View style={styles.centerState}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.centerStateText}>Calculando...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error || !preview || !cobrador) {
    return (
      <SafeAreaView edges={['top']} style={styles.safe}>
        <View style={styles.header}>
          <Pressable onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="chevron-back" size={24} color={colors.white} />
          </Pressable>
          <Text style={styles.headerTitle}>Liquidación</Text>
          <View style={{ width: 40 }} />
        </View>
        <View style={styles.centerState}>
          <Ionicons name="cloud-offline-outline" size={48} color={colors.textMedium} />
          <Text style={styles.errorText}>{error || 'Error desconocido'}</Text>
          <Pressable style={styles.retryButton} onPress={fetchData}>
            <Text style={styles.retryText}>Reintentar</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <Text style={styles.headerTitle}>{cobrador.nombre}</Text>
        <Pressable style={styles.moreButton}>
          <Ionicons name="ellipsis-horizontal" size={22} color={colors.white} />
        </Pressable>
      </View>

      <ScrollView style={styles.scroll} showsVerticalScrollIndicator={false}>
        {/* Profile card */}
        <View style={styles.profileCard}>
          <View style={[styles.avatar, { backgroundColor: cobrador.avatarColor }]}>
            <Text style={styles.avatarText}>{cobrador.initials}</Text>
          </View>
          <Text style={styles.profileName}>{cobrador.nombre}</Text>
          <Text style={styles.profileInfo}>
            Cobrador · {preview.employee.code}
            {cobrador.antiguedad ? ` · ${cobrador.antiguedad}` : ''}
          </Text>

          <View style={styles.progressSection}>
            <View style={styles.progressBar}>
              <View
                style={[
                  styles.progressFill,
                  { width: `${cobrador.porcentajeMeta}%` },
                ]}
              />
            </View>
            <Text style={styles.progressText}>
              {formatMoney(cobrador.totalCobrado)} de {formatMoney(cobrador.metaCobro)} meta
            </Text>
          </View>
        </View>

        {/* Neto card */}
        <View style={styles.netoCard}>
          <Text style={styles.netoLabel}>NETO A PAGAR</Text>
          <Text style={[styles.netoValue, neto < 0 && styles.netoNegative]}>
            {formatMoney(neto)}
          </Text>

          {paid ? (
            <View style={styles.paidBadge}>
              <Ionicons name="checkmark-circle" size={18} color={colors.success} />
              <Text style={styles.paidBadgeText}>Pago registrado</Text>
            </View>
          ) : (
            <Pressable style={styles.payButton} onPress={() => setShowPaymentModal(true)}>
              <Ionicons name="card-outline" size={20} color={colors.white} />
              <Text style={styles.payButtonText}>PAGAR AHORA</Text>
            </Pressable>
          )}
        </View>

        {/* Alerts */}
        {preview.has_alerts && preview.alerts.length > 0 && (
          <View style={styles.alertsCard}>
            {preview.alerts.map((alert, i) => (
              <View key={i} style={styles.alertRow}>
                <Ionicons name="alert-circle" size={16} color={colors.orange} />
                <Text style={styles.alertText}>{alert}</Text>
              </View>
            ))}
          </View>
        )}

        {/* Comisiones section */}
        <Section
          title="COMISIONES"
          total={totalComisiones}
          totalColor={colors.success}
          icon="💰"
        >
          <ComisionRow
            label="Cobranza normal (10%)"
            detail={`${preview.commissions.regular.count} cobros · ${formatMoney(Number(preview.commissions.regular.amount_collected))}`}
            amount={Number(preview.commissions.regular.commission)}
          />
          <ComisionRow
            label="Pagos de contado (5%)"
            detail={`${preview.commissions.cash.count} cobros · ${formatMoney(Number(preview.commissions.cash.amount_collected))}`}
            amount={Number(preview.commissions.cash.commission)}
          />
          <ComisionRow
            label="Entregas ($50 c/u)"
            detail={`${preview.commissions.delivery.count} pólizas/endosos`}
            amount={Number(preview.commissions.delivery.commission)}
            isLast
          />

          <Pressable style={styles.viewAllLink}>
            <Text style={styles.viewAllText}>
              Ver{' '}
              {preview.commissions.regular.count + preview.commissions.cash.count} cobros del período
            </Text>
            <Ionicons name="chevron-forward" size={16} color={colors.primary} />
          </Pressable>
        </Section>

        {/* Deducciones section */}
        <Section
          title="DEDUCCIONES"
          total={-totalDeducciones}
          totalColor={colors.error}
          icon="📉"
        >
          {deducciones.map((item, index) => (
            <DeduccionRow
              key={item.id}
              item={item}
              isLast={index === deducciones.length - 1}
            />
          ))}

          {deducciones.length === 0 && (
            <View style={styles.emptyState}>
              <Ionicons name="checkmark-circle" size={24} color={colors.success} />
              <Text style={styles.emptyText}>Sin deducciones este período ✓</Text>
            </View>
          )}

          {!paid && (
            <Pressable
              style={styles.addDeduccionLink}
              onPress={() => setShowDeduccionModal(true)}
            >
              <Ionicons name="add-circle-outline" size={18} color={colors.primary} />
              <Text style={styles.addDeduccionText}>Agregar deducción manual</Text>
            </Pressable>
          )}
        </Section>

        {/* Historial section */}
        <Section title="HISTORIAL" icon="📜" defaultExpanded={false}>
          {historial.length === 0 && (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>Sin liquidaciones anteriores</Text>
            </View>
          )}

          {historial.map((item) => (
            <View key={item.id} style={styles.historialRow}>
              <View>
                <Text style={styles.historialPeriodo}>{item.period_label}</Text>
                {item.paid_at && (
                  <Text style={styles.historialFecha}>
                    Pagado el{' '}
                    {new Date(item.paid_at).toLocaleDateString('es-MX', {
                      day: 'numeric',
                      month: 'short',
                    })}
                  </Text>
                )}
              </View>
              <View style={styles.historialRight}>
                <Text style={styles.historialMonto}>{formatMoney(Number(item.net_amount))}</Text>
                <Ionicons
                  name={item.status === 'paid' ? 'checkmark-circle' : 'time-outline'}
                  size={16}
                  color={item.status === 'paid' ? colors.success : colors.orange}
                />
              </View>
            </View>
          ))}

          {historial.length > 0 && (
            <Pressable style={styles.viewAllLink}>
              <Text style={styles.viewAllText}>Ver historial completo</Text>
              <Ionicons name="chevron-forward" size={16} color={colors.primary} />
            </Pressable>
          )}
        </Section>

        <View style={{ height: 40 }} />
      </ScrollView>

      {/* Payment Modal */}
      <PaymentModal
        visible={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        onConfirm={handlePaymentConfirm}
        cobrador={cobrador}
        neto={neto}
        periodo={period.label}
      />

      {/* Add Deduccion Modal */}
      <AddDeduccionModal
        visible={showDeduccionModal}
        onClose={() => setShowDeduccionModal(false)}
        onAdd={handleAddDeduccion}
        cobradorNombre={cobrador.nombre}
      />
    </SafeAreaView>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.background,
  },

  // Header
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
  },
  headerTitle: {
    flex: 1,
    fontSize: 18,
    fontWeight: '700',
    color: colors.white,
    textAlign: 'center',
  },
  moreButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'flex-end',
  },

  scroll: { flex: 1 },

  // Center states
  centerState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: spacing.md,
    paddingVertical: spacing['3xl'],
  },
  centerStateText: {
    fontSize: 14,
    color: colors.textMedium,
  },
  errorText: {
    fontSize: 14,
    color: colors.error,
    textAlign: 'center',
    paddingHorizontal: spacing.xl,
  },
  retryButton: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xl,
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    marginTop: spacing.sm,
  },
  retryText: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.white,
  },

  // Profile card
  profileCard: {
    backgroundColor: colors.white,
    margin: spacing.lg,
    padding: spacing.xl,
    borderRadius: radius.lg,
    alignItems: 'center',
    ...cardShadow,
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  avatarText: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.white,
  },
  profileName: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.textDark,
    marginBottom: 4,
  },
  profileInfo: {
    fontSize: 13,
    color: colors.textMedium,
    marginBottom: spacing.lg,
  },
  progressSection: { width: '100%' },
  progressBar: {
    height: 8,
    backgroundColor: colors.border,
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: spacing.sm,
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 4,
  },
  progressText: {
    fontSize: 12,
    color: colors.textMedium,
    textAlign: 'center',
  },

  // Neto card
  netoCard: {
    backgroundColor: colors.white,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    padding: spacing.xl,
    borderRadius: radius.lg,
    alignItems: 'center',
    ...cardShadow,
  },
  netoLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: colors.textMedium,
    letterSpacing: 0.5,
    marginBottom: spacing.sm,
  },
  netoValue: {
    fontSize: 36,
    fontWeight: '700',
    color: colors.primary,
    marginBottom: spacing.lg,
  },
  netoNegative: { color: colors.error },
  payButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing['2xl'],
    borderRadius: radius.md,
    gap: spacing.sm,
    width: '100%',
  },
  payButtonText: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.white,
  },
  paidBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.lg,
    backgroundColor: colors.successBg,
    borderRadius: radius.md,
  },
  paidBadgeText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.success,
  },

  // Alerts
  alertsCard: {
    backgroundColor: colors.orangeBg,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    padding: spacing.lg,
    borderRadius: radius.lg,
    gap: spacing.sm,
    ...cardShadow,
  },
  alertRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  alertText: {
    fontSize: 13,
    color: colors.orange,
    flex: 1,
  },

  // Sections
  section: {
    backgroundColor: colors.white,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    borderRadius: radius.lg,
    overflow: 'hidden',
    ...cardShadow,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  sectionTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  sectionIcon: { fontSize: 16 },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: colors.textMedium,
    letterSpacing: 0.5,
  },
  sectionRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  sectionTotal: {
    fontSize: 14,
    fontWeight: '700',
  },
  sectionContent: { padding: spacing.lg },

  // Comision rows
  comisionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
  },
  comisionRowBorder: {
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  comisionInfo: { flex: 1 },
  comisionLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.textDark,
    marginBottom: 2,
  },
  comisionDetail: {
    fontSize: 12,
    color: colors.textMedium,
  },
  comisionAmount: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.success,
  },
  deduccionAmount: { color: colors.error },

  // Links
  viewAllLink: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: spacing.md,
    marginTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  viewAllText: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.primary,
  },
  addDeduccionLink: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    paddingTop: spacing.md,
    marginTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  addDeduccionText: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.primary,
  },

  // Empty state
  emptyState: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    paddingVertical: spacing.md,
  },
  emptyText: {
    fontSize: 13,
    color: colors.success,
  },

  // Historial
  historialRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  historialPeriodo: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.textDark,
  },
  historialFecha: {
    fontSize: 12,
    color: colors.textMedium,
    marginTop: 2,
  },
  historialRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  historialMonto: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textDark,
  },

  // Modal
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  modalContent: {
    backgroundColor: colors.white,
    borderRadius: radius.xl,
    padding: spacing['3xl'],
    width: '100%',
    maxWidth: 340,
    alignItems: 'center',
  },
  modalAvatar: {
    width: 72,
    height: 72,
    borderRadius: 36,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  modalAvatarText: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.white,
  },
  modalName: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.textDark,
    marginBottom: spacing.sm,
  },
  modalAmount: {
    fontSize: 32,
    fontWeight: '700',
    color: colors.primary,
    marginBottom: spacing.sm,
  },
  modalPeriodo: {
    fontSize: 13,
    color: colors.textMedium,
    marginBottom: spacing['2xl'],
  },
  modalError: {
    fontSize: 13,
    color: colors.error,
    textAlign: 'center',
    marginBottom: spacing.md,
    paddingHorizontal: spacing.sm,
  },
  methodsContainer: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing['2xl'],
  },
  methodButton: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.lg,
    borderRadius: radius.md,
    borderWidth: 2,
    borderColor: colors.border,
    gap: spacing.sm,
  },
  methodSelected: {
    borderColor: colors.primary,
    backgroundColor: colors.primaryBg,
  },
  methodText: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.textMedium,
  },
  methodTextSelected: { color: colors.primary },
  confirmButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing['2xl'],
    borderRadius: radius.md,
    width: '100%',
    gap: spacing.sm,
  },
  confirmButtonDisabled: {
    backgroundColor: colors.textMedium,
    opacity: 0.5,
  },
  confirmButtonText: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.white,
  },
  cancelButton: {
    paddingVertical: spacing.md,
    marginTop: spacing.md,
  },
  cancelButtonText: {
    fontSize: 14,
    color: colors.textMedium,
    fontWeight: '500',
  },

  // Success state
  successContainer: {
    alignItems: 'center',
    paddingVertical: spacing['2xl'],
  },
  successIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.success,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  successTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.textDark,
    marginBottom: spacing.sm,
  },
  successSubtitle: {
    fontSize: 14,
    color: colors.textMedium,
  },
});
