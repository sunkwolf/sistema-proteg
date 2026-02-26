/**
 * Liquidaciones - Vista general de todos los cobradores
 * 
 * Diseño: Claudy ✨
 * Una vista de cartas donde Elena ve TODO de un vistazo.
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  Pressable,
  RefreshControl,
  Animated,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { colors, spacing, radius, cardShadow } from '@/theme';
import { formatMoney } from '@/utils/format';

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
  comisionCobranza: number;    // 10% de cobros normales
  comisionContado: number;     // 5% de contados
  comisionEntregas: number;    // $50 × entregas
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
}

// ─── Mock Data ────────────────────────────────────────────────────────────────

const PERIODO_ACTUAL: Periodo = {
  label: '2da Quincena · Febrero 2026',
  quincena: '2da',
  mes: 2,
  anio: 2026,
};

const COBRADORES_MOCK: CobradorLiquidacion[] = [
  {
    id: '1',
    nombre: 'Edgar Martínez',
    initials: 'EM',
    avatarColor: '#4A3AFF',
    metaCobro: 17000,
    totalCobrado: 13200,
    porcentajeMeta: 78,
    comisionCobranza: 1320,
    comisionContado: 425,
    comisionEntregas: 250,
    totalComisiones: 1995,
    deduccionGasolina: 400,
    deduccionPrestamo: 200,
    deduccionDiferencias: 0,
    totalDeducciones: 600,
    neto: 1395,
    status: 'ready',
    statusMessage: 'Listo para pagar',
  },
  {
    id: '2',
    nombre: 'Laura Jiménez',
    initials: 'LJ',
    avatarColor: '#34C759',
    metaCobro: 15000,
    totalCobrado: 16800,
    porcentajeMeta: 112,
    comisionCobranza: 1680,
    comisionContado: 510,
    comisionEntregas: 150,
    totalComisiones: 2340,
    deduccionGasolina: 350,
    deduccionPrestamo: 0,
    deduccionDiferencias: 100,
    totalDeducciones: 450,
    neto: 1890,
    status: 'ready',
    statusMessage: '¡Superó su meta!',
    superioMeta: true,
  },
  {
    id: '3',
    nombre: 'Carlos Vega',
    initials: 'CV',
    avatarColor: '#FF6B35',
    metaCobro: 14000,
    totalCobrado: 7280,
    porcentajeMeta: 52,
    comisionCobranza: 728,
    comisionContado: 172,
    comisionEntregas: 0,
    totalComisiones: 900,
    deduccionGasolina: 600,
    deduccionPrestamo: 300,
    deduccionDiferencias: 150,
    totalDeducciones: 1050,
    neto: -150,
    status: 'negative',
    statusMessage: 'Saldo negativo — revisar deducciones',
  },
  {
    id: '4',
    nombre: 'Miguel Ruiz',
    initials: 'MR',
    avatarColor: '#8E44AD',
    metaCobro: 12000,
    totalCobrado: 10200,
    porcentajeMeta: 85,
    comisionCobranza: 1020,
    comisionContado: 0,
    comisionEntregas: 100,
    totalComisiones: 1120,
    deduccionGasolina: 280,
    deduccionPrestamo: 0,
    deduccionDiferencias: 0,
    totalDeducciones: 280,
    neto: 840,
    status: 'paid',
    statusMessage: 'Pagado el 28 feb',
    fechaPago: '28 feb',
  },
  {
    id: '5',
    nombre: 'Ana Torres',
    initials: 'AT',
    avatarColor: '#E91E63',
    metaCobro: 13000,
    totalCobrado: 11700,
    porcentajeMeta: 90,
    comisionCobranza: 1170,
    comisionContado: 285,
    comisionEntregas: 100,
    totalComisiones: 1555,
    deduccionGasolina: 320,
    deduccionPrestamo: 150,
    deduccionDiferencias: 0,
    totalDeducciones: 470,
    neto: 1085,
    status: 'ready',
    statusMessage: 'Listo para pagar',
  },
  {
    id: '6',
    nombre: 'Roberto Sánchez',
    initials: 'RS',
    avatarColor: '#00BCD4',
    metaCobro: 16000,
    totalCobrado: 8000,
    porcentajeMeta: 50,
    comisionCobranza: 800,
    comisionContado: 0,
    comisionEntregas: 50,
    totalComisiones: 850,
    deduccionGasolina: 420,
    deduccionPrestamo: 200,
    deduccionDiferencias: 75,
    totalDeducciones: 695,
    neto: 155,
    status: 'alert',
    statusMessage: 'Diferencia sin justificar',
  },
];

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
  const barColor = percentage >= 100 ? colors.success : 
                   percentage >= 70 ? colors.primary : 
                   colors.orange;
  
  return (
    <View style={styles.progressContainer}>
      <View style={styles.progressTrack}>
        <View 
          style={[
            styles.progressFill, 
            { width: `${Math.min(clampedPct, 100)}%`, backgroundColor: barColor }
          ]} 
        />
        {/* Marca del 100% */}
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
      
      {/* Body: Resumen financiero o estado pagado */}
      {isPaid ? (
        <View style={styles.paidContainer}>
          <Ionicons name="checkmark-done" size={16} color={colors.success} />
          <Text style={styles.paidText}>
            Pagado el {item.fechaPago} · {formatMoney(item.neto)}
          </Text>
        </View>
      ) : (
        <>
          {/* Resumen: Comisiones - Deducciones = Neto */}
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
              <Text style={[
                styles.netoValue, 
                isNegative && styles.netoNegative
              ]}>
                {formatMoney(item.neto)}
              </Text>
              <Text style={styles.netoCaption}>NETO</Text>
            </View>
          </View>
          
          {/* Status message */}
          <View style={[
            styles.statusBadge,
            item.status === 'ready' && styles.statusReady,
            item.status === 'alert' && styles.statusAlert,
            item.status === 'negative' && styles.statusNegative,
            item.superioMeta && styles.statusChampion,
          ]}>
            <Text style={[
              styles.statusText,
              item.status === 'ready' && styles.statusTextReady,
              item.status === 'alert' && styles.statusTextAlert,
              item.status === 'negative' && styles.statusTextNegative,
              item.superioMeta && styles.statusTextChampion,
            ]}>
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

// ─── Main Screen ──────────────────────────────────────────────────────────────

export default function LiquidacionesScreen() {
  const router = useRouter();
  const [refreshing, setRefreshing] = useState(false);
  const [periodo, setPeriodo] = useState(PERIODO_ACTUAL);
  const [cobradores, setCobradores] = useState(COBRADORES_MOCK);
  
  // Calcular resumen
  const listos = cobradores.filter(c => c.status === 'ready').length;
  const conAlertas = cobradores.filter(c => c.status === 'alert' || c.status === 'negative').length;
  const pagados = cobradores.filter(c => c.status === 'paid').length;
  const totalListos = cobradores
    .filter(c => c.status === 'ready')
    .reduce((sum, c) => sum + c.neto, 0);
  
  const onRefresh = useCallback(() => {
    setRefreshing(true);
    // TODO: Fetch real data
    setTimeout(() => setRefreshing(false), 1000);
  }, []);
  
  const handleCobradorPress = (cobrador: CobradorLiquidacion) => {
    router.push(`/gerente/liquidaciones/${cobrador.id}`);
  };
  
  const handlePayAll = () => {
    // TODO: Implementar pago masivo
    console.log('Pagar todos los listos');
  };
  
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
      
      {/* Summary bar */}
      <View style={styles.summaryBar}>
        <Text style={styles.summaryBarText}>
          {cobradores.length} cobradores · 
          <Text style={styles.summaryReady}> {listos} listos</Text> · 
          <Text style={styles.summaryAlert}> {conAlertas} con alertas</Text> · 
          <Text style={styles.summaryPaid}> {pagados} pagado{pagados !== 1 ? 's' : ''}</Text>
        </Text>
      </View>
      
      {/* List of cobradores */}
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
        ListFooterComponent={<View style={{ height: 100 }} />}
      />
      
      {/* Bottom action: Pay all ready */}
      {listos > 0 && (
        <View style={styles.bottomAction}>
          <Pressable 
            style={({ pressed }) => [
              styles.payAllButton,
              pressed && styles.payAllPressed,
            ]}
            onPress={handlePayAll}
          >
            <Ionicons name="card-outline" size={20} color={colors.white} />
            <Text style={styles.payAllText}>
              PAGAR TODOS LOS LISTOS ({listos})
            </Text>
            <Text style={styles.payAllAmount}>{formatMoney(totalListos)}</Text>
          </Pressable>
        </View>
      )}
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
    right: '16.67%', // 100/120 = ~83.33%, so mark is at 83.33% from left = 16.67% from right
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
  statusReady: {
    backgroundColor: colors.successBg,
  },
  statusAlert: {
    backgroundColor: colors.orangeBg,
  },
  statusNegative: {
    backgroundColor: colors.errorBg,
  },
  statusChampion: {
    backgroundColor: '#FFF8E1',
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  statusTextReady: {
    color: colors.success,
  },
  statusTextAlert: {
    color: colors.orange,
  },
  statusTextNegative: {
    color: colors.error,
  },
  statusTextChampion: {
    color: '#F9A825',
  },
  
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
