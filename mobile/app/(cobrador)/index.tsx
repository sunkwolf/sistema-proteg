import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Pressable,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { useAuth } from '@/context/AuthContext';
import { Card, Badge } from '@/components/ui';
import { colors, spacing, typography } from '@/theme';
import { formatMoney, formatDateFull } from '@/utils/format';
import { DashboardCobrador } from '@/types';

// TODO: reemplazar con fetch real
const MOCK_DASHBOARD: DashboardCobrador = {
  collector_name: 'Edgar',
  date: new Date().toISOString(),
  cash_pending: '3250.00',
  cash_limit: '5000.00',
  cash_pct: 65,
  summary: {
    collections_count: 8,
    collected_amount: '4100.00',
    pending_approval: 2,
    commission_today: '820.00',
  },
  recent_notifications: [],
};

export default function DashboardCobrador() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [refreshing, setRefreshing] = useState(false);
  const [data, setData] = useState(MOCK_DASHBOARD);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    // TODO: fetch dashboard real
    setTimeout(() => setRefreshing(false), 800);
  }, []);

  const cashPct = data.cash_pct;
  const cashBarColor = cashPct >= 100 ? colors.danger : cashPct >= 80 ? colors.warning : colors.primary;

  return (
    <SafeAreaView edges={['top']} style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Saludo */}
        <Text style={styles.greeting}>
          Buenos días, {user?.name?.split(' ')[0] || data.collector_name} 👋
        </Text>
        <Text style={styles.date}>{formatDateFull(data.date)}</Text>

        {/* Efectivo pendiente */}
        <Card onPress={() => router.push('/(cobrador)/efectivo')} style={styles.cashCard}>
          <Text style={styles.sectionLabel}>EFECTIVO PENDIENTE</Text>
          <Text style={[styles.cashAmount, { color: cashBarColor }]}>
            💵 {formatMoney(data.cash_pending)}
          </Text>
          <Text style={styles.cashSub}>Por entregar</Text>
          <View style={styles.progressBg}>
            <View
              style={[
                styles.progressFill,
                { width: `${Math.min(cashPct, 100)}%`, backgroundColor: cashBarColor },
              ]}
            />
          </View>
          {data.cash_limit && (
            <Text style={styles.cashLimit}>{cashPct}% del tope</Text>
          )}
        </Card>

        {/* Resumen del día */}
        <Text style={styles.sectionLabel}>RESUMEN DEL DÍA</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{data.summary.collections_count}</Text>
            <Text style={styles.statLabel}>Cobros</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{formatMoney(data.summary.collected_amount)}</Text>
            <Text style={styles.statLabel}>Cobrado</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{data.summary.pending_approval}</Text>
            <Text style={styles.statLabel}>Pend. Aprob.</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{formatMoney(data.summary.commission_today)}</Text>
            <Text style={styles.statLabel}>Comisión Hoy</Text>
          </View>
        </View>

        {/* Acciones rápidas */}
        <Text style={styles.sectionLabel}>ACCIONES RÁPIDAS</Text>
        <Pressable
          style={styles.quickAction}
          onPress={() => router.push('/(cobrador)/folios')}
        >
          <Text style={styles.quickActionText}>📋  Mis Folios</Text>
        </Pressable>
        <Pressable
          style={styles.quickAction}
          onPress={() => router.push('/(cobrador)/ruta')}
        >
          <Text style={styles.quickActionText}>🗺️  Mi Ruta</Text>
        </Pressable>
        <Pressable
          style={styles.quickAction}
          onPress={() => router.push('/(cobrador)/propuestas')}
        >
          <Text style={styles.quickActionText}>📊  Mis Propuestas</Text>
        </Pressable>

        {/* Logout (temporal — luego va en menú) */}
        <Pressable onPress={logout} style={styles.logoutBtn}>
          <Text style={styles.logoutText}>Cerrar sesión</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: spacing.lg, paddingBottom: 40 },
  greeting: { ...typography.h2, color: colors.gray900 },
  date: { ...typography.body, color: colors.gray500, marginBottom: spacing.xl },

  cashCard: { marginTop: spacing.sm },
  cashAmount: { ...typography.money, marginTop: spacing.sm },
  cashSub: { ...typography.caption, color: colors.gray500 },
  progressBg: {
    height: 8,
    backgroundColor: colors.gray200,
    borderRadius: 4,
    marginTop: spacing.md,
    overflow: 'hidden',
  },
  progressFill: { height: 8, borderRadius: 4 },
  cashLimit: { ...typography.small, color: colors.gray500, marginTop: spacing.xs },

  sectionLabel: {
    ...typography.captionBold,
    color: colors.gray500,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginTop: spacing['2xl'],
    marginBottom: spacing.md,
  },

  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  statBox: {
    width: '47%',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    alignItems: 'center',
  },
  statValue: { ...typography.moneySmall, color: colors.gray900 },
  statLabel: { ...typography.caption, color: colors.gray500, marginTop: 2 },

  quickAction: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.sm,
  },
  quickActionText: { ...typography.bodyBold, color: colors.primary },

  logoutBtn: {
    alignItems: 'center',
    marginTop: spacing['3xl'],
    padding: spacing.md,
  },
  logoutText: { ...typography.body, color: colors.gray400 },
});
