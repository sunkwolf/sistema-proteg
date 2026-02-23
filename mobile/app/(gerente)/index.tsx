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
import { useAuthStore } from '@/store/auth';
import { Card } from '@/components/ui';
import { colors, spacing, typography } from '@/theme';
import { formatMoney, formatDateFull } from '@/utils/format';

export default function DashboardGerente() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const router = useRouter();
  const [refreshing, setRefreshing] = useState(false);

  // TODO: datos reales
  const pendingApprovals = 5;
  const summary = {
    approved: 28,
    approvedAmount: '33600.00',
    rejected: 3,
    corrected: 2,
  };
  const collectorsWithCash = 2;

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 800);
  }, []);

  return (
    <SafeAreaView edges={['top']} style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <Text style={styles.greeting}>Hola, {user?.name?.split(' ')[0] || 'Elena'} 👋</Text>
        <Text style={styles.date}>{formatDateFull(new Date().toISOString())}</Text>

        {/* Banner pendientes */}
        {pendingApprovals > 0 && (
          <Card
            onPress={() => router.push('/(gerente)/propuestas')}
            style={styles.urgentCard}
          >
            <Text style={styles.urgentText}>
              ⏳ {pendingApprovals} PENDIENTES
            </Text>
            <Text style={styles.urgentSub}>de autorización</Text>
            <Text style={styles.urgentLink}>Revisar ahora →</Text>
          </Card>
        )}

        {/* Resumen */}
        <Text style={styles.sectionLabel}>RESUMEN DEL DÍA</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{summary.approved}</Text>
            <Text style={styles.statLabel}>Aprobados</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{formatMoney(summary.approvedAmount)}</Text>
            <Text style={styles.statLabel}>Cobrado</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{summary.rejected}</Text>
            <Text style={styles.statLabel}>Rechazados</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{summary.corrected}</Text>
            <Text style={styles.statLabel}>Corregidos</Text>
          </View>
        </View>

        {/* Confirmar efectivo */}
        <Card onPress={() => router.push('/(gerente)/efectivo')}>
          <Text style={styles.sectionLabel}>CONFIRMAR EFECTIVO</Text>
          <Text style={styles.detail}>
            {collectorsWithCash} cobradores en oficina hoy
          </Text>
          <Text style={styles.link}>Confirmar →</Text>
        </Card>

        {/* Acciones rápidas */}
        <Text style={styles.sectionLabel}>ACCIONES RÁPIDAS</Text>
        <Pressable style={styles.quickAction} onPress={() => router.push('/(gerente)/propuestas')}>
          <Text style={styles.quickActionText}>📋  Propuestas</Text>
        </Pressable>
        <Pressable style={styles.quickAction} onPress={() => router.push('/(gerente)/efectivo')}>
          <Text style={styles.quickActionText}>💵  Confirmar Efectivo</Text>
        </Pressable>

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

  urgentCard: { backgroundColor: '#FEF3C7', borderLeftWidth: 4, borderLeftColor: colors.warning },
  urgentText: { ...typography.h3, color: colors.warning },
  urgentSub: { ...typography.body, color: colors.gray600 },
  urgentLink: { ...typography.bodyBold, color: colors.primary, marginTop: spacing.sm },

  sectionLabel: {
    ...typography.captionBold,
    color: colors.gray500,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginTop: spacing['2xl'],
    marginBottom: spacing.md,
  },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.md },
  statBox: {
    width: '47%',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    alignItems: 'center',
  },
  statValue: { ...typography.moneySmall, color: colors.gray900 },
  statLabel: { ...typography.caption, color: colors.gray500, marginTop: 2 },

  detail: { ...typography.body, color: colors.gray700 },
  link: { ...typography.bodyBold, color: colors.primary, marginTop: spacing.sm },

  quickAction: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.sm,
  },
  quickActionText: { ...typography.bodyBold, color: colors.primary },

  logoutBtn: { alignItems: 'center', marginTop: spacing['3xl'], padding: spacing.md },
  logoutText: { ...typography.body, color: colors.gray400 },
});
