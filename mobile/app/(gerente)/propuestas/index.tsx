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
import { formatMoney, formatTime } from '@/utils/format';

interface ProposalListItem {
  id: number;
  folio: string;
  client_name: string;
  payment_number: number;
  amount: string;
  method: string;
  collector_name: string;
  created_at: string;
  is_partial: boolean;
  partial_seq?: number;
}

// TODO: datos reales
const MOCK: ProposalListItem[] = [
  { id: 1, folio: '18510', client_name: 'Roberto Sánchez', payment_number: 1, amount: '1401.00', method: 'Efectivo', collector_name: 'Edgar R.', created_at: '2026-02-23T10:15:00-06:00', is_partial: false },
  { id: 2, folio: '18502', client_name: 'Ana González', payment_number: 2, amount: '850.00', method: 'Efectivo', collector_name: 'Jorge L.', created_at: '2026-02-23T09:52:00-06:00', is_partial: true, partial_seq: 1 },
];

export default function PropuestasGerente() {
  const router = useRouter();
  const [refreshing, setRefreshing] = useState(false);
  const [proposals] = useState(MOCK);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 800);
  }, []);

  const renderItem = ({ item }: { item: ProposalListItem }) => (
    <Card onPress={() => router.push(`/(gerente)/propuestas/${item.id}`)}>
      <View style={styles.header}>
        <Badge label="⏳ PENDIENTE" variant="warning" />
        <Text style={styles.time}>{formatTime(item.created_at)}</Text>
      </View>
      <Text style={styles.folio}>F: {item.folio} · Pago #{item.payment_number}</Text>
      <Text style={styles.client}>{item.client_name}</Text>
      <View style={styles.meta}>
        <Text style={styles.metaText}>
          {formatMoney(item.amount)} · {item.method}
          {item.is_partial ? ` · Abono ${item.partial_seq}` : ''}
        </Text>
        <Text style={styles.metaText}>Cobrador: {item.collector_name}</Text>
      </View>
      <Pressable style={styles.reviewBtn}>
        <Text style={styles.reviewText}>Revisar →</Text>
      </Pressable>
    </Card>
  );

  return (
    <SafeAreaView edges={[]} style={styles.container}>
      <Text style={styles.countText}>{proposals.length} pendientes de revisión</Text>
      <FlatList
        data={proposals}
        keyExtractor={(i) => i.id.toString()}
        renderItem={renderItem}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  countText: { ...typography.caption, color: colors.gray500, padding: spacing.lg, paddingBottom: spacing.sm },
  list: { paddingHorizontal: spacing.lg, paddingBottom: 40 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.sm },
  time: { ...typography.caption, color: colors.gray400 },
  folio: { ...typography.bodyBold, color: colors.gray800 },
  client: { ...typography.body, color: colors.gray600 },
  meta: { marginTop: spacing.xs },
  metaText: { ...typography.caption, color: colors.gray500 },
  reviewBtn: { alignSelf: 'flex-end', marginTop: spacing.sm },
  reviewText: { ...typography.captionBold, color: colors.primary },
});
