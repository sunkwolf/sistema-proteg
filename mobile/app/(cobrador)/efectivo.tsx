import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Card } from '@/components/ui';
import { colors, spacing, typography } from '@/theme';
import { formatMoney, formatDateShort } from '@/utils/format';

// TODO: datos reales
const MOCK_DATA = {
  total: '3250.00',
  limit: '5000.00',
  pct: 65,
  items: [
    { date: '2026-02-23', entries: [
      { folio: '18405', client: 'María L.', amount: '1200.00' },
      { folio: '18502', client: 'Ana G.', amount: '850.00' },
    ]},
    { date: '2026-02-22', entries: [
      { folio: '18310', client: 'Luis M.', amount: '1200.00' },
    ]},
  ],
  history: [
    { date: '2026-02-21', amount: '2450.00', confirmed_by: 'Erika' },
  ],
};

export default function EfectivoPendiente() {
  const d = MOCK_DATA;
  const pct = d.pct;
  const barColor = pct >= 100 ? colors.danger : pct >= 80 ? colors.warning : colors.primary;

  return (
    <>
      <SafeAreaView edges={[]} style={styles.container}>
        <ScrollView contentContainerStyle={styles.scroll}>
          {/* Total */}
          <Card style={styles.totalCard}>
            <Text style={styles.sectionTitle}>TOTAL A ENTREGAR</Text>
            <Text style={[styles.totalAmount, { color: barColor }]}>
              💵 {formatMoney(d.total)}
            </Text>
            <Text style={styles.sub}>Sin depositar</Text>
            <View style={styles.progressBg}>
              <View style={[styles.progressFill, { width: `${Math.min(pct, 100)}%`, backgroundColor: barColor }]} />
            </View>
            <Text style={styles.limitText}>Tope: {formatMoney(d.limit!)}</Text>
          </Card>

          {/* Desglose */}
          <Text style={styles.sectionTitle}>DESGLOSE</Text>
          {d.items.map((group) => (
            <View key={group.date}>
              <Text style={styles.groupDate}>
                {group.date === new Date().toISOString().slice(0, 10) ? 'Hoy' : formatDateShort(group.date)}:
              </Text>
              {group.entries.map((e) => (
                <Card key={e.folio}>
                  <View style={styles.entryRow}>
                    <Text style={styles.entryFolio}>F:{e.folio} {e.client}</Text>
                    <Text style={styles.entryAmount}>{formatMoney(e.amount)}</Text>
                  </View>
                  <Text style={styles.entrySub}>Efectivo · Aprobado ✅</Text>
                </Card>
              ))}
            </View>
          ))}

          {/* Historial de entregas */}
          <Text style={[styles.sectionTitle, { marginTop: spacing.xl }]}>HISTORIAL DE ENTREGAS</Text>
          {d.history.map((h) => (
            <Card key={h.date}>
              <View style={styles.entryRow}>
                <Text style={styles.detail}>{formatDateShort(h.date)}: {formatMoney(h.amount)} ✅</Text>
              </View>
              <Text style={styles.entrySub}>Confirmado: {h.confirmed_by}</Text>
            </Card>
          ))}
        </ScrollView>
      </SafeAreaView>
    </>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: spacing.lg, paddingBottom: 40 },
  totalCard: { alignItems: 'center' },
  totalAmount: { ...typography.money, fontSize: 32, marginTop: spacing.sm },
  sub: { ...typography.caption, color: colors.gray500 },
  progressBg: { height: 10, backgroundColor: colors.gray200, borderRadius: 5, width: '100%', marginTop: spacing.md, overflow: 'hidden' },
  progressFill: { height: 10, borderRadius: 5 },
  limitText: { ...typography.small, color: colors.gray400, marginTop: spacing.xs },
  sectionTitle: {
    ...typography.captionBold,
    color: colors.gray500,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginTop: spacing.lg,
    marginBottom: spacing.md,
  },
  groupDate: { ...typography.bodyBold, color: colors.gray700, marginBottom: spacing.sm },
  entryRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  entryFolio: { ...typography.body, color: colors.gray700 },
  entryAmount: { ...typography.bodyBold, color: colors.gray900 },
  entrySub: { ...typography.caption, color: colors.gray400, marginTop: 2 },
  detail: { ...typography.body, color: colors.gray700 },
});
