import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { colors, spacing } from '@/theme';
import { formatMoney, formatDateFull } from '@/utils/format';

type ProposalStatus = 'pending' | 'approved' | 'rejected';

interface Proposal {
  id: string;
  folio: string;
  payment_number: number;
  amount: string;
  method: string;
  status: ProposalStatus;
  time: string;
  reject_reason?: string;
}

const MOCK_PROPOSALS: Proposal[] = [
  { id: '1', folio: '18510', payment_number: 1, amount: '1401.00', method: 'Efectivo', status: 'pending', time: '10:15 AM' },
  { id: '2', folio: '18405', payment_number: 3, amount: '1200.00', method: 'Efectivo', status: 'approved', time: '11:30 AM' },
  { id: '3', folio: '18615', payment_number: 4, amount: '920.00', method: 'Efectivo', status: 'rejected', time: '8:45 AM', reject_reason: 'Recibo incorrecto. La foto no es legible.' },
];

const STATUS_CONFIG: Record<ProposalStatus, { label: string; color: string; bg: string; border: string }> = {
  pending: { label: 'PENDIENTE', color: '#92600A', bg: '#FEF3C7', border: '#FACC15' },
  approved: { label: 'APROBADO', color: '#1B7A34', bg: '#DEF7E4', border: '#34C759' },
  rejected: { label: 'RECHAZADO', color: '#C0281E', bg: '#FEE2E0', border: '#FF3B30' },
};

const FILTERS: { key: string; label: string }[] = [
  { key: 'all', label: 'Todas' },
  { key: 'pending', label: 'Pendientes' },
  { key: 'approved', label: 'Aprobadas' },
  { key: 'rejected', label: 'Rechazadas' },
];

export default function PropuestasScreen() {
  const router = useRouter();
  const [filter, setFilter] = useState('all');
  const proposals = filter === 'all' ? MOCK_PROPOSALS : MOCK_PROPOSALS.filter(p => p.status === filter);

  const approved = MOCK_PROPOSALS.filter(p => p.status === 'approved');
  const pending = MOCK_PROPOSALS.filter(p => p.status === 'pending');
  const rejected = MOCK_PROPOSALS.filter(p => p.status === 'rejected');
  const approvedTotal = approved.reduce((s, p) => s + parseFloat(p.amount), 0);
  const pendingTotal = pending.reduce((s, p) => s + parseFloat(p.amount), 0);

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={{ width: 40 }}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <Text style={styles.headerTitle}>Mis Propuestas</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scroll}>
        {/* Date section */}
        <View style={styles.dateSection}>
          <Text style={styles.dateTitle}>{formatDateFull(new Date().toISOString())}</Text>
          <Text style={styles.dateSubtitle}>{MOCK_PROPOSALS.length} propuestas enviadas</Text>
        </View>

        {/* Filter chips */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filtersRow} contentContainerStyle={{ paddingHorizontal: 16, gap: 8 }}>
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
        </ScrollView>

        {/* Proposal cards */}
        {proposals.map(p => {
          const cfg = STATUS_CONFIG[p.status];
          return (
            <View key={p.id} style={[styles.proposalCard, { borderLeftColor: cfg.border }]}>
              {/* Status + Folio row */}
              <View style={styles.cardTopRow}>
                <View style={[styles.statusBadge, { backgroundColor: cfg.bg }]}>
                  <Text style={[styles.statusText, { color: cfg.color }]}>{cfg.label}</Text>
                </View>
                <Text style={styles.folioText}>F:{p.folio}</Text>
              </View>

              {/* Title */}
              <Text style={styles.cardTitle}>
                Pago #{p.payment_number} - {formatMoney(p.amount)}
              </Text>

              {p.status !== 'rejected' && (
                <>
                  {/* Divider */}
                  <View style={styles.divider} />
                  {/* Method */}
                  <View style={styles.infoRow}>
                    <Text style={styles.infoIcon}>💵</Text>
                    <Text style={styles.infoText}>{p.method}</Text>
                  </View>
                  {/* Divider */}
                  <View style={styles.divider} />
                  {/* Time */}
                  <View style={styles.infoRow}>
                    {p.status === 'approved' ? (
                      <>
                        <Text style={styles.infoIcon}>✅</Text>
                        <Text style={[styles.infoText, { color: '#34C759' }]}>Aprobado {p.time}</Text>
                      </>
                    ) : (
                      <>
                        <Text style={styles.infoIcon}>🕐</Text>
                        <Text style={styles.infoText}>Enviado {p.time}</Text>
                      </>
                    )}
                  </View>
                </>
              )}

              {p.status === 'rejected' && p.reject_reason && (
                <View style={styles.rejectBox}>
                  <View style={styles.rejectHeader}>
                    <Text style={{ fontSize: 14 }}>⚠️</Text>
                    <Text style={styles.rejectTitle}>MOTIVO</Text>
                  </View>
                  <Text style={styles.rejectReason}>{p.reject_reason}</Text>
                </View>
              )}
            </View>
          );
        })}

        <View style={{ height: 80 }} />
      </ScrollView>

      {/* Bottom summary bar */}
      <View style={styles.summaryBar}>
        <View style={styles.summaryCol}>
          <Text style={styles.summaryLabel}>APROBADAS</Text>
          <Text style={[styles.summaryNum, { color: '#34C759' }]}>
            {approved.length} <Text style={styles.summaryAmount}>({formatMoney(String(approvedTotal))})</Text>
          </Text>
        </View>
        <View style={styles.summaryCol}>
          <Text style={styles.summaryLabel}>PENDIENTES</Text>
          <Text style={[styles.summaryNum, { color: '#F5A623' }]}>
            {pending.length} <Text style={styles.summaryAmount}>({formatMoney(String(pendingTotal))})</Text>
          </Text>
        </View>
        <View style={styles.summaryCol}>
          <Text style={styles.summaryLabel}>RECHAZADAS</Text>
          <Text style={[styles.summaryNum, { color: '#FF3B30' }]}>{rejected.length}</Text>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.primary },

  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    backgroundColor: colors.primary,
  },
  backArrow: { fontSize: 22, color: colors.white, fontWeight: '600' },
  headerTitle: { fontSize: 20, fontWeight: '700', color: colors.white },

  scrollView: { flex: 1, backgroundColor: colors.background },
  scroll: { paddingBottom: 20 },

  dateSection: {
    backgroundColor: colors.white,
    paddingHorizontal: 16,
    paddingVertical: 20,
  },
  dateTitle: { fontSize: 26, fontWeight: '700', color: '#1C1C1E' },
  dateSubtitle: { fontSize: 14, color: colors.primary, marginTop: 4 },

  filtersRow: { marginVertical: 12 },
  chip: {
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: '#D1D1D6',
    borderRadius: 20,
    paddingHorizontal: 20,
    paddingVertical: 8,
  },
  chipActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  chipText: { fontSize: 14, color: '#3C3C43' },
  chipTextActive: { color: colors.white, fontWeight: '600' },

  proposalCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 1,
  },
  cardTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 4,
  },
  statusText: { fontSize: 11, fontWeight: '700', letterSpacing: 0.5 },
  folioText: { fontSize: 13, color: '#8E8E93' },
  cardTitle: { fontSize: 20, fontWeight: '700', color: '#1C1C1E', marginTop: 8 },

  divider: { height: 1, backgroundColor: '#E5E5EA', marginVertical: 12 },

  infoRow: { flexDirection: 'row', alignItems: 'center' },
  infoIcon: { fontSize: 14, marginRight: 8 },
  infoText: { fontSize: 14, color: '#6C6C70' },

  rejectBox: {
    backgroundColor: '#FFF0EF',
    borderRadius: 8,
    padding: 12,
    marginTop: 12,
  },
  rejectHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 4 },
  rejectTitle: { fontSize: 12, fontWeight: '700', color: '#1C1C1E', marginLeft: 6, letterSpacing: 0.5 },
  rejectReason: { fontSize: 14, color: '#3C3C43' },

  summaryBar: {
    flexDirection: 'row',
    backgroundColor: colors.white,
    borderTopWidth: 1,
    borderTopColor: '#E5E5EA',
    paddingVertical: 12,
    paddingHorizontal: 8,
  },
  summaryCol: { flex: 1, alignItems: 'center' },
  summaryLabel: { fontSize: 10, color: '#8E8E93', fontWeight: '700', letterSpacing: 0.5, marginBottom: 4 },
  summaryNum: { fontSize: 20, fontWeight: '700' },
  summaryAmount: { fontSize: 12, fontWeight: '400' },
});
