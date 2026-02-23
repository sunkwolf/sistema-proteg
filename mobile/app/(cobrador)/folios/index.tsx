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
import { Card, Badge, Input } from '@/components/ui';
import { colors, spacing, typography, radius } from '@/theme';
import { formatMoney, formatDateShort } from '@/utils/format';
import { FolioCard, OverdueLevel } from '@/types';

const overdueColors: Record<OverdueLevel, string> = {
  high: colors.overdueHigh,
  mid: colors.overdueMid,
  low: colors.overdueLow,
  on_time: colors.onTime,
  collected: colors.collected,
};

const overdueEmoji: Record<OverdueLevel, string> = {
  high: '🔴',
  mid: '🟠',
  low: '🟡',
  on_time: '🟢',
  collected: '⚫',
};

type FilterType = 'todos' | 'pendientes' | 'atrasados';

// TODO: mock data — reemplazar con fetch real
const MOCK_FOLIOS: FolioCard[] = [
  { folio: '18405', client_name: 'María López', payment_number: 3, total_payments: 7, amount: '1200.00', due_date: '2026-02-05', days_overdue: 18, overdue_level: 'high', has_proposal_today: false, proposal_status: null },
  { folio: '18502', client_name: 'Ana González', payment_number: 2, total_payments: 7, amount: '850.00', due_date: '2026-02-12', days_overdue: 11, overdue_level: 'mid', has_proposal_today: false, proposal_status: null },
  { folio: '18510', client_name: 'Roberto Sánchez', payment_number: 1, total_payments: 7, amount: '1401.00', due_date: '2026-02-17', days_overdue: 6, overdue_level: 'low', has_proposal_today: false, proposal_status: null },
  { folio: '18615', client_name: 'Carmen Ruiz', payment_number: 4, total_payments: 7, amount: '920.00', due_date: '2026-02-25', days_overdue: -2, overdue_level: 'on_time', has_proposal_today: false, proposal_status: null },
];

export default function FoliosScreen() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<FilterType>('todos');
  const [refreshing, setRefreshing] = useState(false);
  const [folios] = useState(MOCK_FOLIOS);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 800);
  }, []);

  const filtered = folios.filter((f) => {
    if (search && !f.client_name.toLowerCase().includes(search.toLowerCase()) && !f.folio.includes(search)) return false;
    if (filter === 'pendientes') return f.overdue_level !== 'collected';
    if (filter === 'atrasados') return f.days_overdue > 0;
    return true;
  });

  const renderFolio = ({ item }: { item: FolioCard }) => (
    <Card onPress={() => router.push(`/(cobrador)/folios/${item.folio}`)}>
      <View style={styles.folioHeader}>
        <Text style={styles.folioEmoji}>{overdueEmoji[item.overdue_level]}</Text>
        <Text style={styles.folioNumber}>F: {item.folio}</Text>
        {item.has_proposal_today && (
          <Badge
            label={item.proposal_status || 'enviado'}
            variant={
              item.proposal_status === 'aprobado' ? 'success' :
              item.proposal_status === 'rechazado' ? 'danger' : 'warning'
            }
          />
        )}
      </View>
      <Text style={styles.clientName}>{item.client_name}</Text>
      <View style={styles.folioMeta}>
        <Text style={styles.metaText}>
          Pago {item.payment_number} · {formatMoney(item.amount)}
        </Text>
        <Text style={[
          styles.metaText,
          item.days_overdue > 0 && { color: overdueColors[item.overdue_level] },
        ]}>
          Vence: {formatDateShort(item.due_date)}
          {item.days_overdue > 0 && ` ⚠️`}
        </Text>
      </View>
    </Card>
  );

  return (
    <SafeAreaView edges={[]} style={styles.container}>
      <View style={styles.searchBar}>
        <Input
          placeholder="Buscar folio o nombre"
          value={search}
          onChangeText={setSearch}
          containerStyle={{ marginBottom: 0 }}
        />
      </View>

      <View style={styles.filters}>
        {(['todos', 'pendientes', 'atrasados'] as FilterType[]).map((f) => (
          <Pressable
            key={f}
            onPress={() => setFilter(f)}
            style={[styles.filterChip, filter === f && styles.filterChipActive]}
          >
            <Text style={[styles.filterText, filter === f && styles.filterTextActive]}>
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </Text>
          </Pressable>
        ))}
      </View>

      <Text style={styles.count}>{filtered.length} folios asignados</Text>

      <FlatList
        data={filtered}
        keyExtractor={(item) => item.folio}
        renderItem={renderFolio}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  searchBar: { padding: spacing.lg, paddingBottom: 0 },
  filters: {
    flexDirection: 'row',
    gap: spacing.sm,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  filterChip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
    backgroundColor: colors.gray100,
  },
  filterChipActive: { backgroundColor: colors.primary },
  filterText: { ...typography.caption, color: colors.gray600 },
  filterTextActive: { color: colors.white },
  count: {
    ...typography.caption,
    color: colors.gray500,
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.sm,
  },
  list: { paddingHorizontal: spacing.lg, paddingBottom: 20 },
  folioHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.xs,
  },
  folioEmoji: { fontSize: 14 },
  folioNumber: { ...typography.bodyBold, color: colors.gray800, flex: 1 },
  clientName: { ...typography.body, color: colors.gray700 },
  folioMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing.xs,
  },
  metaText: { ...typography.caption, color: colors.gray500 },
});
