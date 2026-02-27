/**
 * Liquidaciones - Vista general de todos los cobradores
 *
 * Diseño: Claudy ✨
 * Una vista de cartas donde Elena ve TODO de un vistazo.
 * Conectado a la API real el 2026-02-27.
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  Pressable,
  RefreshControl,
  ActivityIndicator,
  Modal,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { colors, spacing, radius, cardShadow } from '@/theme';
import { formatMoney } from '@/utils/format';
import {
  getAllPreviews,
  createBatchSettlement,
  toApiMethod,
  type SettlementPreview,
} from '@/api/settlements';

// ─── Types ────────────────────────────────────────────────────────────────────

type LiquidacionStatus = 'ready' | 'alert' | 'paid' | 'negative';

interface CobradorLiquidacion {
  id: string;
  nombre: string;
  initials: string;
  avatarColor: string;

  // Progreso
  metaCobro: number;
  totalCobrado: number;
  porcentajeMeta: number;

  // Comisiones
  comisionCobranza: number;
  comisionContado: number;
  comisionEntregas: number;
  totalComisiones: number;

  // Deducciones
  deduccionGasolina: number;
  deduccionPrestamo: number;
  deduccionDiferencias: number;
  totalDeducciones: number;

  // Resumen
  neto: number;
  status: LiquidacionStatus;
  statusMessage: string;

  // Si ya pagado
  fechaPago?: string;
  superioMeta?: boolean;
}

interface Periodo {
  label: string;
  quincena: '1ra' | '2da';
  mes: number;
  anio: number;
  start: string;
  end: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

const AVATAR_COLORS = [
  '#6D28D9', '#D97706', '#4F46E5', '#059669',
  '#DC2626', '#2563EB', '#7C3AED', '#DB2777',
];

const MONTHS_ES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
];

function getCurrentPeriod(): Periodo {
  const now = new Date();
  const day = now.getDate();
  const month = now.getMonth() + 1;
  const year = now.getFullYear();
  const mm = String(month).padStart(2, '0');

  if (day <= 5) {
    // Si es muy temprano en el mes (1-5), mostrar 2da quincena del mes anterior
    const lastMonthDate = new Date(year, month - 2, 1);
    const lm = lastMonthDate.getMonth() + 1;
    const ly = lastMonthDate.getFullYear();
    const lmm = String(lm).padStart(2, '0');
    const lastDay = new Date(ly, lm, 0).getDate();
    return {
      label: `2da Quincena · ${MONTHS_ES[lm - 1]} ${ly}`,
      quincena: '2da',
      mes: lm,
      anio: ly,
      start: `${ly}-${lmm}-16`,
      end: `${ly}-${lmm}-${lastDay}`,
    };
  }

  if (day <= 20) {
    return {
      label: `1ra Quincena · ${MONTHS_ES[month - 1]} ${year}`,
      quincena: '1ra',
      mes: month,
      anio: year,
      start: `${year}-${mm}-01`,
      end: `${year}-${mm}-15`,
    };
  } else {
    const lastDay = new Date(year, month, 0).getDate();
    return {
      label: `2da Quincena · ${MONTHS_ES[month - 1]} ${year}`,
      quincena: '2da',
      mes: month,
      anio: year,
      start: `${year}-${mm}-16`,
      end: `${year}-${mm}-${lastDay}`,
    };
  }
}

function getInitials(fullName: string): string {
  const parts = fullName.trim().split(' ');
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  return parts[0].slice(0, 2).toUpperCase();
}

function previewToLiquidacion(preview: SettlementPreview, index: number): CobradorLiquidacion {
  const net = Number(preview.net_amount);
  const superioMeta = preview.goal_percentage >= 100;

  // Agrupar deducciones por tipo
  const deductions = preview.deductions.items;
  const fuelTotal = deductions
    .filter((d) => d.type === 'fuel')
    .reduce((s, d) => s + Number(d.amount), 0);
  const loanTotal = deductions
    .filter((d) => d.type === 'loan')
    .reduce((s, d) => s + Number(d.amount), 0);
  const otherTotal = deductions
    .filter((d) => d.type !== 'fuel' && d.type !== 'loan')
    .reduce((s, d) => s + Number(d.amount), 0);

  // Determinar status y mensaje
  let status: LiquidacionStatus;
  let statusMessage: string;

  if (net < 0) {
    status = 'negative';
    statusMessage = 'Saldo negativo — revisar deducciones';
  } else if (preview.has_alerts) {
    status = 'alert';
    statusMessage = preview.alerts[0] || 'Tiene alertas pendientes';
  } else {
    status = 'ready';
    statusMessage = superioMeta ? '¡Superó su meta!' : 'Listo para pagar';
  }

  return {
    id: String(preview.employee.employee_role_id),
    nombre: preview.employee.full_name,
    initials: getInitials(preview.employee.full_name),
    avatarColor: AVATAR_COLORS[index % AVATAR_COLORS.length],
    metaCobro: Number(preview.goal_amount),
    totalCobrado: Number(preview.total_collected),
    porcentajeMeta: Math.round(preview.goal_percentage),
    comisionCobranza: Number(preview.commissions.regular.commission),
    comisionContado: Number(preview.commissions.cash.commission),
    comisionEntregas: Number(preview.commissions.delivery.commission),
    totalComisiones: Number(preview.commissions.total),
    deduccionGasolina: fuelTotal,
    deduccionPrestamo: loanTotal,
    deduccionDiferencias: otherTotal,
    totalDeducciones: Number(preview.deductions.total),
    neto: net,
    status,
    statusMessage,
    superioMeta,
  };
}

// ─── Components ───────────────────────────────────────────────────────────────

function StatusIcon({ status, superioMeta }: { status: LiquidacionStatus; superioMeta?: boolean }) {
  if (superioMeta) {
    return <Text style={styles.statusIcon}>🏆</Text>;
  }

  switch (status) {
    case 'ready':
      return <Ionicons name="checkmark-circle" size={20} color={colors.success} />;
    case 'paid':
      return <Ionicons name="checkmark-done" size={20} color={colors.success} />;
    case 'alert':
      return <Ionicons name="alert-circle" size={20} color={colors.orange} />;
    case 'negative':
      return <Ionicons name="warning" size={20} color={colors.error} />;
    default:
      return null;
  }
}

function ProgressBar({ percentage, status }: { percentage: number; status: LiquidacionStatus }) {
  const clampedPct = Math.min(percentage, 120);
  const barColor =
    percentage >= 100 ? colors.success : percentage >= 70 ? colors.primary : colors.orange;

  return (
    <View style={styles.progressContainer}>
      <View style={styles.progressTrack}>
        <View
          style={[
            styles.progressFill,
            { width: `${Math.min(clampedPct, 100)}%`, backgroundColor: barColor },
          ]}
        />
        <View style={styles.progressMark} />
      </View>
      <Text style={[styles.progressText, { color: barColor }]}>{percentage}%</Text>
    </View>
  );
}

function CobradorCard({ item, onPress }: { item: CobradorLiquidacion; onPress: () => void }) {
  const isPaid = item.status === 'paid';
  const isNegative = item.neto < 0;

  return (
    <Pressable
      style={({ pressed }) => [
        styles.card,
        pressed && styles.cardPressed,
        isPaid && styles.cardPaid,
      ]}
      onPress={onPress}
    >
      {/* Header: Avatar + Nombre + Status Icon */}
      <View style={styles.cardHeader}>
        <View style={[styles.avatar, { backgroundColor: item.avatarColor }]}>
          <Text style={styles.avatarText}>{item.initials}</Text>
        </View>
        <View style={styles.cardHeaderInfo}>
          <Text style={styles.cardName}>{item.nombre}</Text>
          {!isPaid && <ProgressBar percentage={item.porcentajeMeta} status={item.status} />}
        </View>
        <StatusIcon status={item.status} superioMeta={item.superioMeta} />
      </View>

      {/* Body */}
      {isPaid ? (
        <View style={styles.paidContainer}>
          <Ionicons name="checkmark-done" size={16} color={colors.success} />
          <Text style={styles.paidText}>
            Pagado el {item.fechaPago} · {formatMoney(item.neto)}
          </Text>
        </View>
      ) : (
        <>
          <View style={styles.summaryRow}>
            <View style={styles.summaryItem}>
              <Text style={styles.summaryLabel}>💰</Text>
              <Text style={styles.summaryValue}>{formatMoney(item.totalComisiones)}</Text>
              <Text style={styles.summaryCaption}>comisiones</Text>
            </View>

            <View style={styles.summaryItem}>
              <Text style={styles.summaryLabel}>📉</Text>
              <Text style={[styles.summaryValue, styles.deductionValue]}>
                -{formatMoney(item.totalDeducciones)}
              </Text>
              <Text style={styles.summaryCaption}>deducciones</Text>
            </View>

            <View style={styles.summaryDivider} />

            <View style={[styles.summaryItem, styles.summaryNeto]}>
              <Text style={[styles.netoValue, isNegative && styles.netoNegative]}>
                {formatMoney(item.neto)}
              </Text>
              <Text style={styles.netoCaption}>NETO</Text>
            </View>
          </View>

          <View
            style={[
              styles.statusBadge,
              item.status === 'ready' && styles.statusReady,
              item.status === 'alert' && styles.statusAlert,
              item.status === 'negative' && styles.statusNegative,
              item.superioMeta && styles.statusChampion,
            ]}
          >
            <Text
              style={[
                styles.statusText,
                item.status === 'ready' && styles.statusTextReady,
                item.status === 'alert' && styles.statusTextAlert,
                item.status === 'negative' && styles.statusTextNegative,
                item.superioMeta && styles.statusTextChampion,
              ]}
            >
              {item.status === 'ready' && '🟢 '}
              {item.status === 'alert' && '🟡 '}
              {item.status === 'negative' && '🔴 '}
              {item.statusMessage}
            </Text>
          </View>
        </>
      )}
    </Pressable>
  );
}

// ─── Pay All Modal ────────────────────────────────────────────────────────────

function PayAllModal({
  visible,
  onClose,
  onConfirm,
  cobradores,
  total,
}: {
  visible: boolean;
  onClose: () => void;
  onConfirm: (method: string) => void;
  cobradores: CobradorLiquidacion[];
  total: number;
}) {
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null);
  const [confirming, setConfirming] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleConfirm = () => {
    if (!selectedMethod) return;
    setConfirming(true);

    setTimeout(() => {
      setSuccess(true);
      setTimeout(() => {
        onConfirm(selectedMethod);
        setSuccess(false);
        setConfirming(false);
        setSelectedMethod(null);
      }, 2000);
    }, 500);
  };

  const handleClose = () => {
    setSelectedMethod(null);
    setSuccess(false);
    setConfirming(false);
    onClose();
  };

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={handleClose}>
      <View style={modalStyles.overlay}>
        <View style={modalStyles.content}>
          {success ? (
            <View style={modalStyles.successContainer}>
              <View style={modalStyles.successIcon}>
                <Ionicons name="checkmark" size={48} color={colors.white} />
              </View>
              <Text style={modalStyles.successTitle}>¡Misión Cumplida! ✨</Text>
              <Text style={modalStyles.successSubtitle}>
                {cobradores.length} liquidaciones registradas · {formatMoney(total)}
              </Text>
              <Text style={modalStyles.successCaption}>Elena, el equipo te lo agradece. 💜</Text>
              <View style={modalStyles.successList}>
                {cobradores.map((c) => (
                  <Text key={c.id} style={modalStyles.successName}>
                    ✓ {c.nombre}
                  </Text>
                ))}
              </View>
            </View>
          ) : (
            <>
              <View style={modalStyles.header}>
                <Ionicons name="wallet" size={32} color={colors.primary} />
                <Text style={modalStyles.title}>Pagar a todos los listos</Text>
              </View>

              <Text style={modalStyles.amount}>{formatMoney(total)}</Text>
              <Text style={modalStyles.periodo}>2da Quincena · Feb 2026</Text>

              <View style={modalStyles.cobradoresList}>
                <Text style={modalStyles.listTitle}>{cobradores.length} COBRADORES</Text>
                <ScrollView style={modalStyles.listScroll} nestedScrollEnabled>
                  {cobradores.map((c) => (
                    <View key={c.id} style={modalStyles.cobradorRow}>
                      <View
                        style={[modalStyles.miniAvatar, { backgroundColor: c.avatarColor }]}
                      >
                        <Text style={modalStyles.miniAvatarText}>{c.initials}</Text>
                      </View>
                      <Text style={modalStyles.cobradorName}>{c.nombre}</Text>
                      <Text style={modalStyles.cobradorNeto}>{formatMoney(c.neto)}</Text>
                    </View>
                  ))}
                </ScrollView>
              </View>

              <Text style={modalStyles.methodLabel}>MÉTODO DE PAGO</Text>
              <View style={modalStyles.methodsContainer}>
                <Pressable
                  style={[
                    modalStyles.methodButton,
                    selectedMethod === 'efectivo' && modalStyles.methodSelected,
                  ]}
                  onPress={() => setSelectedMethod('efectivo')}
                >
                  <Ionicons
                    name="cash-outline"
                    size={22}
                    color={selectedMethod === 'efectivo' ? colors.primary : colors.textMedium}
                  />
                  <Text
                    style={[
                      modalStyles.methodText,
                      selectedMethod === 'efectivo' && modalStyles.methodTextSelected,
                    ]}
                  >
                    Efectivo
                  </Text>
                </Pressable>

                <Pressable
                  style={[
                    modalStyles.methodButton,
                    selectedMethod === 'transferencia' && modalStyles.methodSelected,
                  ]}
                  onPress={() => setSelectedMethod('transferencia')}
                >
                  <Ionicons
                    name="phone-portrait-outline"
                    size={22}
                    color={
                      selectedMethod === 'transferencia' ? colors.primary : colors.textMedium
                    }
                  />
                  <Text
                    style={[
                      modalStyles.methodText,
                      selectedMethod === 'transferencia' && modalStyles.methodTextSelected,
                    ]}
                  >
                    Transferencia
                  </Text>
                </Pressable>
              </View>

              <Pressable
                style={[
                  modalStyles.confirmButton,
                  !selectedMethod && modalStyles.confirmButtonDisabled,
                ]}
                onPress={handleConfirm}
                disabled={!selectedMethod || confirming}
              >
                {confirming ? (
                  <Text style={modalStyles.confirmButtonText}>Procesando...</Text>
                ) : (
                  <>
                    <Ionicons name="checkmark-circle" size={20} color={colors.white} />
                    <Text style={modalStyles.confirmButtonText}>
                      CONFIRMAR {cobradores.length} PAGOS
                    </Text>
                  </>
                )}
              </Pressable>

              <Pressable style={modalStyles.cancelButton} onPress={handleClose}>
                <Text style={modalStyles.cancelButtonText}>Cancelar</Text>
              </Pressable>
            </>
          )}
        </View>
      </View>
    </Modal>
  );
}

// ─── Modal Styles ─────────────────────────────────────────────────────────────

const modalStyles = StyleSheet.create({
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
    maxWidth: 360,
    maxHeight: '85%',
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
  amount: {
    fontSize: 36,
    fontWeight: '700',
    color: colors.primary,
    textAlign: 'center',
  },
  periodo: {
    fontSize: 13,
    color: colors.textMedium,
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  cobradoresList: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.lg,
  },
  listTitle: {
    fontSize: 10,
    fontWeight: '700',
    color: colors.textMedium,
    letterSpacing: 0.5,
    marginBottom: spacing.sm,
  },
  listScroll: {
    maxHeight: 150,
  },
  cobradorRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  miniAvatar: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  miniAvatarText: {
    fontSize: 10,
    fontWeight: '700',
    color: colors.white,
  },
  cobradorName: {
    flex: 1,
    fontSize: 13,
    fontWeight: '500',
    color: colors.textDark,
    marginLeft: spacing.sm,
  },
  cobradorNeto: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.primary,
  },
  methodLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: colors.textMedium,
    letterSpacing: 0.5,
    marginBottom: spacing.sm,
  },
  methodsContainer: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.lg,
  },
  methodButton: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    borderWidth: 2,
    borderColor: colors.border,
    gap: spacing.xs,
  },
  methodSelected: {
    borderColor: colors.primary,
    backgroundColor: colors.primaryBg,
  },
  methodText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.textMedium,
  },
  methodTextSelected: {
    color: colors.primary,
  },
  confirmButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    paddingVertical: spacing.lg,
    borderRadius: radius.md,
    gap: spacing.sm,
  },
  confirmButtonDisabled: {
    backgroundColor: colors.textMedium,
    opacity: 0.5,
  },
  confirmButtonText: {
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
  successContainer: {
    alignItems: 'center',
    paddingVertical: spacing.xl,
  },
  successIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.success,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  successTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.textDark,
    marginBottom: 4,
  },
  successSubtitle: {
    fontSize: 14,
    color: colors.textMedium,
    marginBottom: 2,
  },
  successCaption: {
    fontSize: 12,
    color: colors.primary,
    fontStyle: 'italic',
    marginBottom: spacing.lg,
  },
  successList: {
    alignItems: 'center',
  },
  successName: {
    fontSize: 13,
    color: colors.success,
    fontWeight: '500',
    marginVertical: 2,
  },
});

// ─── Main Screen ──────────────────────────────────────────────────────────────

export default function LiquidacionesScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [periodo, setPeriodo] = useState<Periodo>(getCurrentPeriod);
  const [cobradores, setCobradores] = useState<CobradorLiquidacion[]>([]);
  const [showPayAllModal, setShowPayAllModal] = useState(false);

  // ── Fetch data ────────────────────────────────────────────────────────────

  const fetchData = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const previews = await getAllPreviews(periodo.start, periodo.end);
      setCobradores(previews.map(previewToLiquidacion));
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'No se pudieron cargar las liquidaciones');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [periodo.start, periodo.end]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // ── Handlers ──────────────────────────────────────────────────────────────

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchData(true);
  }, [fetchData]);

  const handleCobradorPress = (cobrador: CobradorLiquidacion) => {
    router.push(`/(gerente)/liquidaciones/${cobrador.id}`);
  };

  const handlePayAll = () => {
    setShowPayAllModal(true);
  };

  const handlePayAllConfirm = async (method: string) => {
    const listos = cobradores.filter((c) => c.status === 'ready');
    try {
      await createBatchSettlement({
        employee_role_ids: listos.map((c) => parseInt(c.id, 10)),
        period_start: periodo.start,
        period_end: periodo.end,
        payment_method: toApiMethod(method),
      });

      // Actualizar UI localmente (luego refresh revalida contra el servidor)
      const hoy = new Date();
      const fechaPago = `${hoy.getDate()} ${['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'][hoy.getMonth()]}`;
      setCobradores((prev) =>
        prev.map((c) =>
          c.status === 'ready'
            ? {
                ...c,
                status: 'paid' as LiquidacionStatus,
                fechaPago,
                statusMessage: `Pagado el ${fechaPago}`,
              }
            : c,
        ),
      );
    } catch (err: any) {
      // El modal ya cerró — mostrar error como estado en pantalla
      setError(err?.response?.data?.detail || 'Error al registrar los pagos');
    }
    setShowPayAllModal(false);
  };

  // ── Derived state ─────────────────────────────────────────────────────────

  const cobradoresListos = cobradores.filter((c) => c.status === 'ready');
  const listos = cobradoresListos.length;
  const conAlertas = cobradores.filter(
    (c) => c.status === 'alert' || c.status === 'negative',
  ).length;
  const pagados = cobradores.filter((c) => c.status === 'paid').length;
  const totalListos = cobradoresListos.reduce((sum, c) => sum + c.neto, 0);

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <Text style={styles.headerTitle}>Liquidaciones</Text>
        <Pressable style={styles.settingsButton}>
          <Ionicons name="options-outline" size={22} color={colors.white} />
        </Pressable>
      </View>

      {/* Periodo selector */}
      <Pressable style={styles.periodoSelector}>
        <Ionicons name="calendar-outline" size={18} color={colors.primary} />
        <Text style={styles.periodoText}>{periodo.label}</Text>
        <Ionicons name="chevron-down" size={18} color={colors.textMedium} />
      </Pressable>

      {/* Loading state */}
      {loading && (
        <View style={styles.centerState}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.centerStateText}>Calculando liquidaciones...</Text>
        </View>
      )}

      {/* Error state */}
      {!loading && error && (
        <View style={styles.centerState}>
          <Ionicons name="cloud-offline-outline" size={48} color={colors.textMedium} />
          <Text style={styles.errorText}>{error}</Text>
          <Pressable style={styles.retryButton} onPress={() => fetchData()}>
            <Text style={styles.retryText}>Reintentar</Text>
          </Pressable>
        </View>
      )}

      {/* Data */}
      {!loading && !error && (
        <>
          {/* Summary bar */}
          <View style={styles.summaryBar}>
            <Text style={styles.summaryBarText}>
              {cobradores.length} cobradores ·
              <Text style={styles.summaryReady}> {listos} listos</Text> ·
              <Text style={styles.summaryAlert}> {conAlertas} con alertas</Text> ·
              <Text style={styles.summaryPaid}>
                {' '}
                {pagados} pagado{pagados !== 1 ? 's' : ''}
              </Text>
            </Text>
          </View>

          <FlatList
            data={cobradores}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <CobradorCard item={item} onPress={() => handleCobradorPress(item)} />
            )}
            contentContainerStyle={styles.listContent}
            refreshControl={
              <RefreshControl
                refreshing={refreshing}
                onRefresh={onRefresh}
                tintColor={colors.primary}
              />
            }
            showsVerticalScrollIndicator={false}
            ListEmptyComponent={
              <View style={styles.centerState}>
                <Ionicons name="people-outline" size={48} color={colors.textMedium} />
                <Text style={styles.centerStateText}>Sin cobradores activos</Text>
              </View>
            }
            ListFooterComponent={<View style={{ height: 100 }} />}
          />
        </>
      )}

      {/* Bottom action: Pay all ready */}
      {!loading && !error && listos > 0 && (
        <View style={styles.bottomAction}>
          <Pressable
            style={({ pressed }) => [styles.payAllButton, pressed && styles.payAllPressed]}
            onPress={handlePayAll}
          >
            <Ionicons name="card-outline" size={20} color={colors.white} />
            <Text style={styles.payAllText}>PAGAR TODOS LOS LISTOS ({listos})</Text>
            <Text style={styles.payAllAmount}>{formatMoney(totalListos)}</Text>
          </Pressable>
        </View>
      )}

      {/* Pay All Modal */}
      <PayAllModal
        visible={showPayAllModal}
        onClose={() => setShowPayAllModal(false)}
        onConfirm={handlePayAllConfirm}
        cobradores={cobradoresListos}
        total={totalListos}
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
  settingsButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'flex-end',
  },

  // Periodo
  periodoSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.white,
    marginHorizontal: spacing.lg,
    marginTop: spacing.lg,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xl,
    borderRadius: radius.md,
    gap: spacing.sm,
    ...cardShadow,
  },
  periodoText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textDark,
  },

  // Summary bar
  summaryBar: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  summaryBarText: {
    fontSize: 12,
    color: colors.textMedium,
  },
  summaryReady: { color: colors.success },
  summaryAlert: { color: colors.orange },
  summaryPaid: { color: colors.textMedium },

  // List
  listContent: {
    paddingHorizontal: spacing.lg,
  },

  // Card
  card: {
    backgroundColor: colors.white,
    borderRadius: radius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
    ...cardShadow,
  },
  cardPressed: {
    opacity: 0.92,
    transform: [{ scale: 0.985 }],
  },
  cardPaid: {
    opacity: 0.7,
  },

  // Card header
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.white,
  },
  cardHeaderInfo: {
    flex: 1,
    marginLeft: spacing.md,
  },
  cardName: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.textDark,
    marginBottom: 4,
  },
  statusIcon: {
    fontSize: 20,
  },

  // Progress bar
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  progressTrack: {
    flex: 1,
    height: 6,
    backgroundColor: colors.border,
    borderRadius: 3,
    overflow: 'hidden',
    position: 'relative',
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
  },
  progressMark: {
    position: 'absolute',
    right: '16.67%',
    top: -2,
    bottom: -2,
    width: 2,
    backgroundColor: colors.textMedium,
    opacity: 0.3,
  },
  progressText: {
    fontSize: 11,
    fontWeight: '700',
    width: 36,
    textAlign: 'right',
  },

  // Summary row
  summaryRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
    paddingTop: spacing.sm,
  },
  summaryItem: {
    alignItems: 'center',
    flex: 1,
  },
  summaryLabel: {
    fontSize: 16,
    marginBottom: 2,
  },
  summaryValue: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.textDark,
  },
  deductionValue: {
    color: colors.error,
  },
  summaryCaption: {
    fontSize: 10,
    color: colors.textMedium,
    marginTop: 2,
  },
  summaryDivider: {
    width: 1,
    height: 36,
    backgroundColor: colors.border,
    marginHorizontal: spacing.sm,
  },
  summaryNeto: {
    flex: 1.2,
  },
  netoValue: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.primary,
  },
  netoNegative: {
    color: colors.error,
  },
  netoCaption: {
    fontSize: 10,
    fontWeight: '600',
    color: colors.textMedium,
    letterSpacing: 0.5,
    marginTop: 2,
  },

  // Status badge
  statusBadge: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: radius.sm,
    alignSelf: 'flex-start',
  },
  statusReady: { backgroundColor: colors.successBg },
  statusAlert: { backgroundColor: colors.orangeBg },
  statusNegative: { backgroundColor: colors.errorBg },
  statusChampion: { backgroundColor: '#FFF8E1' },
  statusText: { fontSize: 12, fontWeight: '600' },
  statusTextReady: { color: colors.success },
  statusTextAlert: { color: colors.orange },
  statusTextNegative: { color: colors.error },
  statusTextChampion: { color: '#F9A825' },

  // Paid state
  paidContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    paddingTop: spacing.sm,
  },
  paidText: {
    fontSize: 13,
    color: colors.success,
    fontWeight: '500',
  },

  // Center states (loading / error / empty)
  centerState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: spacing['3xl'],
    gap: spacing.md,
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

  // Bottom action
  bottomAction: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: spacing.lg,
    backgroundColor: colors.white,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    ...cardShadow,
  },
  payAllButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    paddingVertical: spacing.lg,
    borderRadius: radius.md,
    gap: spacing.sm,
  },
  payAllPressed: {
    opacity: 0.85,
  },
  payAllText: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.white,
  },
  payAllAmount: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.white,
    opacity: 0.9,
  },
});
