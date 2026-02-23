import React from 'react';
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
import { LinearGradient } from 'expo-linear-gradient';
import { useAuthStore } from '@/store/auth';
import { SectionHeader, StatCard, QuickAction, Card } from '@/components/ui';
import { colors, spacing, typography } from '@/theme';
import { formatMoney, formatDateFull } from '@/utils/format';
import { DashboardCobrador as DashboardCobradorData } from '@/types';

// TODO: reemplazar con useDashboard() de TanStack Query
const MOCK: DashboardCobradorData = {
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
  const user = useAuthStore((s) => s.user);
  const router = useRouter();
  const [refreshing, setRefreshing] = React.useState(false);
  const d = MOCK;

  const onRefresh = React.useCallback(async () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 800);
  }, []);

  return (
    <SafeAreaView edges={['top']} style={styles.screen}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable>
          <Text style={styles.hamburger}>☰</Text>
        </Pressable>
        <Text style={styles.headerTitle}>Proteg-rt</Text>
        <Pressable onPress={() => router.push('/(cobrador)/notificaciones' as any)}>
          <Text style={styles.bellIcon}>🔔</Text>
          <View style={styles.badge}>
            <Text style={styles.badgeText}>2</Text>
          </View>
        </Pressable>
      </View>

      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Saludo */}
        <View style={styles.greetingBox}>
          <Text style={typography.h1}>
            Buenos días, {user?.name?.split(' ')[0] || d.collector_name} 👋
          </Text>
          <Text style={styles.dateText}>{formatDateFull(d.date)}</Text>
        </View>

        {/* ── Tarjeta de Efectivo (diseño V2 — aprobado) ── */}
        <View style={styles.cashSection}>
          <LinearGradient
            colors={['#4A3AFF', '#6C5CE7']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.cashCard}
          >
            <View style={styles.cashTop}>
              <View style={styles.cashBadge}>
                <Text style={styles.cashBadgeText}>EFECTIVO EN MANO</Text>
              </View>
              <View style={styles.cashChip}>
                <Text style={styles.cashChipText}>Por entregar</Text>
              </View>
            </View>

            <Text style={styles.cashAmount}>
              {formatMoney(d.cash_pending)} <Text style={styles.cashCurrency}>MXN</Text>
            </Text>

            <View style={styles.progressRow}>
              <Text style={styles.progressLabel}>Progreso del límite</Text>
              <Text style={styles.progressPct}>{d.cash_pct}%</Text>
            </View>
            <View style={styles.progressBg}>
              <LinearGradient
                colors={['#4CAF50', '#4A3AFF']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={[styles.progressFill, { width: `${Math.min(d.cash_pct, 100)}%` }]}
              />
            </View>
            <Text style={styles.cashLimitText}>
              Tope: {formatMoney(d.cash_limit || '5000.00')}
            </Text>
          </LinearGradient>
        </View>

        {/* ── Resumen del Día ── */}
        <View style={styles.padded}>
          <SectionHeader title="Resumen del Día" />
          <View style={styles.statsGrid}>
            <StatCard
              icon="📋" iconBg={colors.primaryBg} iconColor={colors.primary}
              label="Cobros" value={String(d.summary.collections_count)}
            />
            <StatCard
              icon="💵" iconBg={colors.successBg} iconColor={colors.success}
              label="Cobrado" value={formatMoney(d.summary.collected_amount)}
            />
            <StatCard
              icon="🚩" iconBg={colors.orangeBg} iconColor={colors.orange}
              label="Pend. Aprob." value={String(d.summary.pending_approval)}
            />
            <StatCard
              icon="💰" iconBg={colors.primaryBg} iconColor={colors.primary}
              label="Comisión Hoy" value={formatMoney(d.summary.commission_today)}
            />
          </View>

          {/* ── Acciones Rápidas ── */}
          <SectionHeader title="Acciones Rápidas" />
          <QuickAction
            icon="📋"
            title="Mis Folios"
            subtitle="Gestión de documentos asignados"
            onPress={() => router.push('/(cobrador)/folios')}
          />
          <QuickAction
            icon="🗺️"
            title="Mi Ruta"
            subtitle="Planificador de visitas del día"
            onPress={() => router.push('/(cobrador)/ruta')}
          />
          <QuickAction
            icon="📊"
            title="Mis Propuestas"
            subtitle="Estado de cobros enviados"
            onPress={() => router.push('/(cobrador)/propuestas')}
          />

          {/* ── Actividad Reciente ── */}
          <SectionHeader title="Actividad Reciente" actionText="Ver todas" onAction={() => {}} />
          <Card>
            <View style={styles.activityItem}>
              <View style={[styles.activityIcon, { backgroundColor: colors.successBg }]}>
                <Text>✅</Text>
              </View>
              <View style={styles.activityText}>
                <Text style={styles.activityTitle}>Pago F:18501 aprobado</Text>
                <Text style={styles.activitySub}>Hace 15 min · Sistema</Text>
              </View>
            </View>
            <View style={styles.activityDivider} />
            <View style={styles.activityItem}>
              <View style={[styles.activityIcon, { backgroundColor: colors.errorBg }]}>
                <Text>❌</Text>
              </View>
              <View style={styles.activityText}>
                <Text style={styles.activityTitle}>Pago F:18405 rechazado</Text>
                <Text style={styles.activitySub}>Hace 1h · Supervisor</Text>
              </View>
              <Pressable style={styles.verBtn}>
                <Text style={styles.verText}>Ver</Text>
              </Pressable>
            </View>
          </Card>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },

  // Header
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 14,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  hamburger: { fontSize: 22, color: colors.textDark },
  headerTitle: { fontSize: 20, fontWeight: '700', color: colors.primary },
  bellIcon: { fontSize: 22 },
  badge: {
    position: 'absolute',
    top: -4,
    right: -6,
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: colors.badgeRed,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeText: { fontSize: 10, fontWeight: '700', color: colors.white },

  scroll: { paddingBottom: 100 },

  // Greeting
  greetingBox: {
    paddingHorizontal: 20,
    paddingTop: 24,
    paddingBottom: 16,
    backgroundColor: colors.white,
  },
  dateText: { fontSize: 14, color: colors.textMedium, marginTop: 4 },

  // Cash card (V2 style)
  cashSection: { paddingHorizontal: 20, marginTop: 16 },
  cashCard: {
    borderRadius: 20,
    paddingHorizontal: 24,
    paddingVertical: 24,
  },
  cashTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cashBadge: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 8,
  },
  cashBadgeText: {
    fontSize: 11,
    fontWeight: '700',
    color: colors.white,
    letterSpacing: 0.5,
  },
  cashChip: {
    backgroundColor: 'rgba(255,255,255,0.15)',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  cashChipText: {
    fontSize: 12,
    fontWeight: '500',
    color: 'rgba(255,255,255,0.9)',
  },
  cashAmount: {
    fontSize: 42,
    fontWeight: '800',
    color: colors.white,
    marginTop: 16,
  },
  cashCurrency: {
    fontSize: 18,
    fontWeight: '500',
    color: 'rgba(255,255,255,0.7)',
  },
  progressRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
  },
  progressLabel: {
    fontSize: 13,
    fontWeight: '500',
    color: 'rgba(255,255,255,0.8)',
  },
  progressPct: {
    fontSize: 13,
    fontWeight: '700',
    color: colors.white,
  },
  progressBg: {
    marginTop: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: 'rgba(255,255,255,0.25)',
    overflow: 'hidden',
  },
  progressFill: {
    height: 8,
    borderRadius: 4,
  },
  cashLimitText: {
    marginTop: 8,
    fontSize: 12,
    fontWeight: '400',
    color: 'rgba(255,255,255,0.7)',
  },

  // Stats
  padded: { paddingHorizontal: 20 },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },

  // Activity
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 14,
  },
  activityDivider: {
    height: 1,
    backgroundColor: colors.divider,
  },
  activityIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  activityText: {
    marginLeft: 12,
    flex: 1,
  },
  activityTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.textDark,
  },
  activitySub: {
    fontSize: 12,
    color: colors.textMedium,
    marginTop: 2,
  },
  verBtn: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E0E0EA',
    backgroundColor: '#FAFAFA',
  },
  verText: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.primary,
  },
});
