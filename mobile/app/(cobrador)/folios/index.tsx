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
import { Ionicons } from '@expo/vector-icons';
import { Card, Badge, Input } from '@/components/ui';
import { colors, spacing, radius } from '@/theme';
import { formatMoney, formatDateShort, formatDateFull } from '@/utils/format';
import { FolioCard, OverdueLevel } from '@/types';

const borderColors: Record<OverdueLevel, string> = {
  high: colors.overdueHigh,
  mid: colors.overdueMid,
  low: colors.overdueLow,
  on_time: colors.onTime,
  collected: colors.collected,
};

const statusIcons: Record<OverdueLevel, { icon: string; bg: string }> = {
  high: { icon: '⚠️', bg: colors.errorBg },
  mid: { icon: '🕐', bg: colors.orangeBg },
  low: { icon: '📅', bg: '#FEF9C3' },
  on_time: { icon: '✅', bg: colors.successBg },
  collected: { icon: '✓', bg: '#F0F0F5' },
};

type FilterType = 'todos' | 'pendientes' | 'atrasados';

// TODO: mock → useFolios()
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

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 800);
  }, []);

  const filtered = MOCK_FOLIOS.filter((f) => {
    if (search && !f.client_name.toLowerCase().includes(search.toLowerCase()) && !f.folio.includes(search)) return false;
    if (filter === 'pendientes') return f.overdue_level !== 'collected';
    if (filter === 'atrasados') return f.days_overdue > 0;
    return true;
  });

  const renderFolio = ({ item }: { item: FolioCard }) => {
    const si = statusIcons[item.overdue_level];
    return (
      <Card
        leftBorderColor={borderColors[item.overdue_level]}
        onPress={() => router.push(`/(cobrador)/folios/${item.folio}`)}
      >
        <View style={styles.folioTop}>
          <View style={styles.folioLeft}>
            <Badge label={`F:${item.folio}`} variant="info" />
            {item.has_proposal_today && (
              <Badge
                label={item.proposal_status || 'enviado'}
                variant={item.proposal_status === 'aprobado' ? 'success' : item.proposal_status === 'rechazado' ? 'danger' : 'warning'}
              />
            )}
          </View>
          <View style={[styles.statusDot, { backgroundColor: si.bg }]}>
            <Text style={{ fontSize: 12 }}>{si.icon}</Text>
          </View>
        </View>
        <Text style={styles.clientName}>{item.client_name}</Text>
        <View style={styles.folioMeta}>
          <Text style={styles.metaLabel}>ETAPA: Pago {item.payment_number}</Text>
          <Text style={styles.metaLabel}>MONTO</Text>
        </View>
        <View style={styles.folioMeta}>
          <Text style={styles.dueDateText}>
            Vence: {formatDateShort(item.due_date)}
            {item.days_overdue > 0 && ` (${item.days_overdue}d)`}
          </Text>
          <Text style={styles.amountText}>{formatMoney(item.amount)}</Text>
        </View>
      </Card>
    );
  };

  return (
    <SafeAreaView edges={['top']} style={styles.screen}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.replace('/(cobrador)')} style={{ width: 40 }}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <Text style={styles.headerTitle}>Mis Folios</Text>
        <View style={{ width: 40 }} />
      </View>

      {/* Date section */}
      <View style={styles.dateSection}>
        <Text style={styles.dateTitle}>{formatDateFull(new Date().toISOString())}</Text>
        <Text style={styles.dateSubtitle}>{filtered.length} folios asignados</Text>
      </View>

      <View style={styles.searchBar}>
        <Input
          placeholder="Buscar folio o cliente"
          value={search}
          onChangeText={setSearch}
          containerStyle={{ marginBottom: 0 }}
        />
      </View>

      {/* Filtros */}
      <View style={styles.filters}>
        {(['todos', 'pendientes', 'atrasados'] as FilterType[]).map((f) => (
          <Pressable
            key={f}
            onPress={() => setFilter(f)}
            style={[styles.chip, filter === f ? styles.chipActive : styles.chipInactive]}
          >
            <Text style={[styles.chipText, filter === f && styles.chipTextActive]}>
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </Text>
          </Pressable>
        ))}
      </View>

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
  screen: { flex: 1, backgroundColor: colors.background },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: colors.primary,
  },
  headerTitle: { fontSize: 20, fontWeight: '700', color: colors.white, textAlign: 'center', flex: 1 },
  dateSection: {
    backgroundColor: colors.white,
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  dateTitle: { fontSize: 22, fontWeight: '700', color: '#1C1C1E' },
  dateSubtitle: { fontSize: 13, color: colors.primary, marginTop: 2 },
  searchBar: { paddingHorizontal: 20, paddingTop: 12 },
  filters: {
    flexDirection: 'row',
    gap: 8,
    paddingHorizontal: 20,
    paddingVertical: 12,
  },
  chip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: radius.full,
  },
  chipActive: { backgroundColor: colors.primary },
  chipInactive: { backgroundColor: colors.white, borderWidth: 1, borderColor: colors.border },
  chipText: { fontSize: 13, fontWeight: '600', color: colors.textMedium },
  chipTextActive: { color: colors.white, fontWeight: '700' },
  list: { paddingHorizontal: 20, paddingBottom: 100 },
  folioTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  folioLeft: { flexDirection: 'row', gap: 8 },
  statusDot: { width: 28, height: 28, borderRadius: 14, justifyContent: 'center', alignItems: 'center' },
  clientName: { fontSize: 16, fontWeight: '700', color: colors.textDark, marginBottom: 8 },
  folioMeta: { flexDirection: 'row', justifyContent: 'space-between' },
  metaLabel: { fontSize: 11, fontWeight: '700', color: colors.textMedium, letterSpacing: 0.3 },
  dueDateText: { fontSize: 14, color: colors.textMedium, marginTop: 2 },
  amountText: { fontSize: 18, fontWeight: '800', color: colors.textDark, marginTop: 2 },
});
