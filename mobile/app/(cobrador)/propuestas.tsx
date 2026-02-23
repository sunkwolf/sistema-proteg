import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  Pressable,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Card, Badge } from '@/components/ui';
import { colors, spacing, typography, radius } from '@/theme';
import { formatMoney, formatTime, formatDateFull } from '@/utils/format';
import { Proposal, ProposalStatus } from '@/types';

const statusConfig: Record<ProposalStatus, { label: string; variant: 'warning' | 'success' | 'danger' | 'info'; icon: string }> = {
  pendiente: { label: 'PENDIENTE', variant: 'warning', icon: '⏳' },
  aprobado: { label: 'APROBADO', variant: 'success', icon: '✅' },
  rechazado: { label: 'RECHAZADO', variant: 'danger', icon: '❌' },
  corregido: { label: 'CORREGIDO', variant: 'info', icon: '🔧' },
};

type FilterType = 'todas' | 'pendiente' | 'aprobado' | 'rechazado';

// TODO: mock data
const MOCK_PROPOSALS: Proposal[] = [
  { id: 1, folio: '18510', client_name: 'Roberto Sánchez', payment_number: 1, amount: '1401.00', method: 'efectivo', receipt_number: 'A00147', receipt_photo_url: null, status: 'pendiente', rejection_reason: null, created_at: '2026-02-23T10:15:00-06:00', reviewed_at: null, reviewed_by: null, is_partial: false, partial_seq: null },
  { id: 2, folio: '18405', client_name: 'María López', payment_number: 3, amount: '1200.00', method: 'efectivo', receipt_number: 'A00148', receipt_photo_url: null, status: 'aprobado', rejection_reason: null, created_at: '2026-02-23T09:30:00-06:00', reviewed_at: '2026-02-23T11:30:00-06:00', reviewed_by: 'Elena', is_partial: false, partial_seq: null },
  { id: 3, folio: '18615', client_name: 'Carmen Ruiz', payment_number: 4, amount: '920.00', method: 'efectivo', receipt_number: 'A0234', receipt_photo_url: null, status: 'rechazado', rejection_reason: 'Recibo incorrecto (#A0234)', created_at: '2026-02-23T08:45:00-06:00', reviewed_at: '2026-02-23T10:00:00-06:00', reviewed_by: 'Elena', is_partial: false, partial_seq: null },
];

export default function MisPropuestas() {
  const router = useRouter();
  const [filter, setFilter] = useState<FilterType>('todas');
  const [refreshing, setRefreshing] = useState(false);
  const [proposals] = useState(MOCK_PROPOSALS);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 800);
  }, []);

  const filtered = proposals.filter((p) =>
    filter === 'todas' ? true : p.status === filter
  );

  const summary = {
    aprobadas: proposals.filter(p => p.status === 'aprobado').length,
    montoAprobado: proposals.filter(p => p.status === 'aprobado').reduce((acc, p) => acc + parseFloat(p.amount), 0),
    pendientes: proposals.filter(p => p.status === 'pendiente').length,
    montoPendiente: proposals.filter(p => p.status === 'pendiente').reduce((acc, p) => acc + parseFloat(p.amount), 0),
    rechazadas: proposals.filter(p => p.status === 'rechazado').length,
  };

  const renderProposal = ({ item }: { item: Proposal }) => {
    const cfg = statusConfig[item.status];
    return (
      <Card>
        <View style={styles.proposalHeader}>
          <Badge label={`${cfg.icon} ${cfg.label}`} variant={cfg.variant} />
          <Text style={styles.time}>{formatTime(item.created_at)}</Text>
        </View>
        <Text style={styles.folioText}>F: {item.folio} · Pago #{item.payment_number}</Text>
        <Text style={styles.detail}>{formatMoney(item.amount)} · {item.method}</Text>
        {item.status === 'rechazado' && item.rejection_reason && (
          <View style={styles.rejectionBox}>
            <Text style={styles.rejectionText}>Motivo: "{item.rejection_reason}"</Text>
            <Pressable
              onPress={() => router.push({
                pathname: '/(cobrador)/cobros/nuevo',
                params: { folio: item.folio },
              })}
            >
              <Text style={styles.correctLink}>Corregir y reenviar →</Text>
            </Pressable>
          </View>
        )}
      </Card>
    );
  };

  return (
    <SafeAreaView edges={[]} style={styles.container}>
      <Text style={styles.dateHeader}>{formatDateFull(new Date().toISOString())}</Text>
      <Text style={styles.count}>{proposals.length} propuestas enviadas</Text>

      {/* Filtros */}
      <View style={styles.filters}>
        {(['todas', 'pendiente', 'aprobado', 'rechazado'] as FilterType[]).map((f) => (
          <Pressable
            key={f}
            onPress={() => setFilter(f)}
            style={[styles.chip, filter === f && styles.chipActive]}
          >
            <Text style={[styles.chipText, filter === f && styles.chipTextActive]}>
              {f === 'todas' ? 'Todas' : f === 'pendiente' ? 'Pend.' : f.charAt(0).toUpperCase() + f.slice(1) + 's'}
            </Text>
          </Pressable>
        ))}
      </View>

      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderProposal}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListFooterComponent={
          <Card style={{ marginTop: spacing.lg }}>
            <Text style={styles.summaryTitle}>RESUMEN DEL DÍA</Text>
            <Text style={styles.summaryRow}>Aprobadas: {summary.aprobadas}   {formatMoney(summary.montoAprobado)}</Text>
            <Text style={styles.summaryRow}>Pendientes: {summary.pendientes}   {formatMoney(summary.montoPendiente)}</Text>
            <Text style={styles.summaryRow}>Rechazadas: {summary.rechazadas}</Text>
          </Card>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  dateHeader: { ...typography.h3, color: colors.gray900, paddingHorizontal: spacing.lg, paddingTop: spacing.lg },
  count: { ...typography.caption, color: colors.gray500, paddingHorizontal: spacing.lg, marginBottom: spacing.sm },
  filters: {
    flexDirection: 'row',
    gap: spacing.sm,
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.md,
  },
  chip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
    backgroundColor: colors.gray100,
  },
  chipActive: { backgroundColor: colors.primary },
  chipText: { ...typography.caption, color: colors.gray600 },
  chipTextActive: { color: colors.white },
  list: { paddingHorizontal: spacing.lg, paddingBottom: 40 },
  proposalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  time: { ...typography.caption, color: colors.gray400 },
  folioText: { ...typography.bodyBold, color: colors.gray800 },
  detail: { ...typography.caption, color: colors.gray500, marginTop: 2 },
  rejectionBox: {
    marginTop: spacing.sm,
    padding: spacing.md,
    backgroundColor: colors.dangerLight,
    borderRadius: radius.sm,
  },
  rejectionText: { ...typography.caption, color: colors.danger },
  correctLink: { ...typography.captionBold, color: colors.primary, marginTop: spacing.sm },
  summaryTitle: {
    ...typography.captionBold,
    color: colors.gray500,
    textTransform: 'uppercase',
    marginBottom: spacing.sm,
  },
  summaryRow: { ...typography.body, color: colors.gray700, marginBottom: 2 },
});
