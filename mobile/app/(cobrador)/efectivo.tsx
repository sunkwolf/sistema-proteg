import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { colors, spacing } from '@/theme';
import { formatMoney } from '@/utils/format';

interface CashEntry {
  folio: string;
  client: string;
  amount: string;
  method: string;
  approved: boolean;
}

interface DeliveryHistory {
  date: string;
  confirmed_by: string;
  amount: string;
}

const MOCK = {
  total: '3250.00',
  limit: '5000.00',
  pct: 65,
  today: [
    { folio: '18405', client: 'María L.', amount: '1200.00', method: 'Efectivo', approved: true },
    { folio: '18502', client: 'Ana G.', amount: '850.00', method: 'Efectivo', approved: true },
  ] as CashEntry[],
  yesterday: [
    { folio: '18310', client: 'Luis M.', amount: '1200.00', method: 'Efectivo', approved: true },
  ] as CashEntry[],
  history: [
    { date: '18/Feb', confirmed_by: 'Erika', amount: '2450.00' },
  ] as DeliveryHistory[],
};

export default function EfectivoScreen() {
  const router = useRouter();

  const renderEntry = (entry: CashEntry, idx: number) => (
    <View key={idx} style={styles.entryCard}>
      <View style={styles.entryLeft}>
        <View style={styles.entryTitleRow}>
          <Text style={styles.entryFolio}>F:{entry.folio}</Text>
          <Text style={styles.entryDot}>•</Text>
          <Text style={styles.entryClient}>{entry.client}</Text>
        </View>
        <View style={styles.entryBadgeRow}>
          <View style={styles.methodBadge}>
            <Text style={styles.methodBadgeText}>{entry.method}</Text>
          </View>
          {entry.approved && (
            <Text style={styles.approvedText}>Aprobado ✅</Text>
          )}
        </View>
      </View>
      <Text style={styles.entryAmount}>{formatMoney(entry.amount)}</Text>
    </View>
  );

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={{ width: 40 }}>
          <Text style={styles.backArrow}>←</Text>
        </Pressable>
        <Text style={styles.headerTitle}>Efectivo Pendiente</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scroll}>
        {/* Summary card */}
        <View style={styles.summaryCard}>
          <View style={styles.moneyIcon}>
            <Text style={{ fontSize: 36 }}>💰</Text>
          </View>
          <Text style={styles.summaryLabel}>Sin depositar</Text>
          <Text style={styles.summaryAmount}>{formatMoney(MOCK.total)}</Text>

          <View style={styles.limitRow}>
            <Text style={styles.limitPct}>{MOCK.pct}% del límite</Text>
            <Text style={styles.limitTope}>Tope: {formatMoney(MOCK.limit)}</Text>
          </View>
          <View style={styles.progressTrack}>
            <View style={[styles.progressFill, { width: `${Math.min(MOCK.pct, 100)}%` }]} />
          </View>
        </View>

        {/* HOY */}
        <Text style={styles.sectionDate}>HOY ({new Date().toLocaleDateString('es-MX', { day: '2-digit', month: 'short' }).toUpperCase()})</Text>
        {MOCK.today.map(renderEntry)}

        {/* AYER */}
        <Text style={styles.sectionDate}>AYER (19/FEB)</Text>
        {MOCK.yesterday.map(renderEntry)}

        {/* Divider */}
        <View style={styles.sectionDivider} />

        {/* Historial */}
        <View style={styles.historyHeader}>
          <Text style={styles.historyTitle}>Historial de Entregas</Text>
          <Pressable>
            <Text style={styles.historyLink}>Ver todo</Text>
          </Pressable>
        </View>

        {MOCK.history.map((h, i) => (
          <View key={i} style={styles.historyCard}>
            <View>
              <Text style={styles.historyDate}>{h.date}</Text>
              <View style={{ flexDirection: 'row', alignItems: 'center', marginTop: 4 }}>
                <Text style={{ fontSize: 14, marginRight: 4 }}>✅</Text>
                <Text style={styles.historyConfirm}>Confirmado: {h.confirmed_by}</Text>
              </View>
            </View>
            <View style={{ alignItems: 'flex-end' }}>
              <Text style={styles.historyLabel}>Entregado</Text>
              <Text style={styles.historyAmount}>{formatMoney(h.amount)}</Text>
            </View>
          </View>
        ))}

        <View style={{ height: 40 }} />
      </ScrollView>
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
  headerTitle: { fontSize: 18, fontWeight: '700', color: colors.white },

  scrollView: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: 16 },

  // Summary card
  summaryCard: {
    backgroundColor: colors.white,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#EEE',
    padding: 24,
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  moneyIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#FFF8E1',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  summaryLabel: { fontSize: 14, color: '#888', marginBottom: 4 },
  summaryAmount: { fontSize: 36, fontWeight: '800', color: '#1A1A1A', marginBottom: 16 },
  limitRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    marginBottom: 8,
  },
  limitPct: { fontSize: 13, fontWeight: '600', color: colors.primary },
  limitTope: { fontSize: 13, color: '#666' },
  progressTrack: {
    width: '100%',
    height: 8,
    backgroundColor: '#E8E8E8',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#22C55E',
    borderRadius: 4,
  },

  // Sections
  sectionDate: {
    fontSize: 13,
    fontWeight: '700',
    color: '#888',
    letterSpacing: 0.5,
    marginBottom: 12,
    marginTop: 4,
  },

  // Entry cards
  entryCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#EEE',
    borderLeftWidth: 3,
    borderLeftColor: '#22C55E',
    padding: 16,
    marginBottom: 12,
  },
  entryLeft: { flex: 1 },
  entryTitleRow: { flexDirection: 'row', alignItems: 'center' },
  entryFolio: { fontSize: 15, fontWeight: '700', color: '#1A1A1A' },
  entryDot: { fontSize: 15, color: '#CCC', marginHorizontal: 6 },
  entryClient: { fontSize: 15, color: '#555' },
  entryBadgeRow: { flexDirection: 'row', alignItems: 'center', marginTop: 6, gap: 8 },
  methodBadge: {
    backgroundColor: '#F0F0F0',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  methodBadgeText: { fontSize: 11, color: '#555', fontWeight: '500' },
  approvedText: { fontSize: 13, color: '#22C55E', fontWeight: '600' },
  entryAmount: { fontSize: 20, fontWeight: '700', color: '#1A1A1A' },

  // Divider
  sectionDivider: { height: 1, backgroundColor: '#E8E8E8', marginVertical: 20 },

  // History
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  historyTitle: { fontSize: 18, fontWeight: '700', color: '#1A1A1A' },
  historyLink: { fontSize: 14, fontWeight: '600', color: colors.primary },

  historyCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#EEE',
    padding: 16,
    marginBottom: 12,
  },
  historyDate: { fontSize: 13, color: '#888' },
  historyConfirm: { fontSize: 14, color: '#333', fontWeight: '500' },
  historyLabel: { fontSize: 12, color: '#999' },
  historyAmount: { fontSize: 20, fontWeight: '700', color: '#22C55E' },
});
