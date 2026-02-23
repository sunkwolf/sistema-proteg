import React, { useState } from 'react';
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
import { colors, spacing, radius } from '@/theme';
import { formatMoney, formatTime } from '@/utils/format';

interface ProposalItem {
  id: number;
  folio: string;
  client_name: string;
  payment_number: number;
  amount: string;
  method: string;
  collector_name: string;
  collector_initial: string;
  created_at: string;
  is_partial: boolean;
  partial_seq?: number;
  is_overdue?: boolean;
  overdue_text?: string;
}

const MOCK: ProposalItem[] = [
  { id: 1, folio: '18510', client_name: 'Roberto Sánchez', payment_number: 1, amount: '1401.00', method: 'Efectivo', collector_name: 'Edgar R.', collector_initial: 'ER', created_at: '2026-02-23T10:15:00-06:00', is_partial: false },
  { id: 2, folio: '18502', client_name: 'Ana González', payment_number: 2, amount: '850.00', method: 'Efectivo', collector_name: 'Jorge L.', collector_initial: 'JL', created_at: '2026-02-23T09:52:00-06:00', is_partial: true, partial_seq: 1 },
  { id: 3, folio: '18320', client_name: 'Pedro Martínez', payment_number: 5, amount: '1100.00', method: 'Transferencia', collector_name: 'Edgar R.', collector_initial: 'ER', created_at: '2026-02-21T14:30:00-06:00', is_partial: false, is_overdue: true, overdue_text: 'Hace 2 días' },
];

export default function PropuestasGerente() {
  const router = useRouter();
  const [refreshing, setRefreshing] = useState(false);

  const renderItem = ({ item }: { item: ProposalItem }) => (
    <Card onPress={() => router.push(`/(gerente)/propuestas/${item.id}`)}>
      <View style={styles.cardTop}>
        <Badge label="● Pendiente" variant="success" />
        <Text style={item.is_overdue ? styles.timestampOverdue : styles.timestamp}>
          {item.is_overdue ? item.overdue_text : formatTime(item.created_at)}
        </Text>
      </View>
      <Text style={styles.clientName}>{item.client_name}</Text>
      <Text style={styles.detail}>
        Pago #{item.payment_number} · {formatMoney(item.amount)}
        {item.is_partial ? ` · Abono ${item.partial_seq}` : ''}
      </Text>
      <View style={styles.methodRow}>
        <Text style={styles.methodIcon}>
          {item.method === 'Efectivo' ? '💵' : item.method === 'Transferencia' ? '📱' : '🏦'}
        </Text>
        <Text style={styles.methodText}>{item.method}</Text>
      </View>
      <View style={styles.collectorRow}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{item.collector_initial}</Text>
        </View>
        <Text style={styles.collectorName}>{item.collector_name}</Text>
        <Pressable style={{ marginLeft: 'auto' }}>
          <Text style={styles.reviewLink}>Revisar →</Text>
        </Pressable>
      </View>
    </Card>
  );

  return (
    <SafeAreaView edges={['top']} style={styles.screen}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()}>
          <Text style={styles.backArrow}>←</Text>
        </Pressable>
        <Text style={styles.headerTitle}>Propuestas</Text>
        <Text style={styles.filterIcon}>☰</Text>
      </View>

      <View style={styles.filterRow}>
        <Text style={styles.filterLabel}>Estado: <Text style={styles.filterValue}>Pendientes ▼</Text></Text>
        <Text style={styles.filterLabel}>Cobrador: <Text style={styles.filterValue}>Todos ▼</Text></Text>
      </View>
      <Text style={styles.countText}>{MOCK.length} pendientes de revisión</Text>

      <FlatList
        data={MOCK}
        keyExtractor={(i) => i.id.toString()}
        renderItem={renderItem}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => {
          setRefreshing(true); setTimeout(() => setRefreshing(false), 800);
        }} />}
        ListFooterComponent={
          MOCK.some(p => p.is_overdue) ? (
            <Pressable style={styles.warningBanner}>
              <Text style={styles.warningText}>⚠️ 1 propuesta &gt;48h sin revisar</Text>
              <Text style={styles.warningChevron}>›</Text>
            </Pressable>
          ) : null
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 20, paddingVertical: 14, backgroundColor: colors.primary,
  },
  backArrow: { fontSize: 22, color: colors.white },
  headerTitle: { fontSize: 18, fontWeight: '700', color: colors.white },
  filterIcon: { fontSize: 20, color: colors.white },
  filterRow: {
    flexDirection: 'row', gap: 16, paddingHorizontal: 20, paddingTop: 16, paddingBottom: 4,
  },
  filterLabel: { fontSize: 14, color: '#6B7280' },
  filterValue: { fontWeight: '600', color: colors.primary },
  countText: { fontSize: 13, color: colors.textMedium, paddingHorizontal: 20, marginBottom: 12 },
  list: { paddingHorizontal: 20, paddingBottom: 100 },

  cardTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  timestamp: { fontSize: 13, color: colors.textLight },
  timestampOverdue: { fontSize: 13, fontWeight: '600', color: colors.error },
  clientName: { fontSize: 18, fontWeight: '700', color: colors.textDark, marginBottom: 4 },
  detail: { fontSize: 14, color: '#6B7280', marginBottom: 8 },
  methodRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 12 },
  methodIcon: { fontSize: 16 },
  methodText: { fontSize: 14, color: '#6B7280' },
  collectorRow: { flexDirection: 'row', alignItems: 'center', paddingTop: 12, borderTopWidth: 1, borderTopColor: colors.divider },
  avatar: {
    width: 32, height: 32, borderRadius: 16, backgroundColor: colors.primaryBg,
    justifyContent: 'center', alignItems: 'center', marginRight: 8,
  },
  avatarText: { fontSize: 12, fontWeight: '700', color: colors.primary },
  collectorName: { fontSize: 14, fontWeight: '500', color: colors.textDark },
  reviewLink: { fontSize: 15, fontWeight: '600', color: colors.primary },
  warningBanner: {
    backgroundColor: '#FFF3DC', borderRadius: 12, padding: 16, marginTop: 12,
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
  },
  warningText: { fontSize: 14, fontWeight: '600', color: '#E8922A' },
  warningChevron: { fontSize: 20, color: '#E8922A' },
});
