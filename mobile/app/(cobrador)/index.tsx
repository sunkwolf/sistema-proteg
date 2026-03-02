import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Pressable,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuthStore } from '@/store/auth';
import { SectionHeader, StatCard, QuickAction, Card } from '@/components/ui';
import { Feather, Ionicons } from '@expo/vector-icons';
import { colors, spacing, typography } from '@/theme';
import { formatMoney, formatDateFull } from '@/utils/format';
import { useDashboard } from '@/hooks/useCollections';

export default function DashboardCobrador() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const router = useRouter();

  // TODO: extract collector_code from JWT user once auth is connected
  const { data: d, isLoading, refetch, isRefetching } = useDashboard();

  const onRefresh = React.useCallback(async () => {
    await refetch();
  }, [refetch]);

  if (isLoading) {
    return (
      <SafeAreaView edges={['top']} style={[styles.screen, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={{ marginTop: 12, color: colors.textMedium }}>Cargando dashboard...</Text>
      </SafeAreaView>
    );
  }

  // Fallback if no data
  const dashboard = d || {
    collector_name: user?.name || 'Cobrador',
    date: new Date().toISOString(),
    cash_pending: '0.00',
    cash_limit: '5000.00',
    cash_pct: 0,
    summary: {
      collections_count: 0,
      collected_amount: '0.00',
      pending_approval: 0,
      commission_today: '0.00',
    },
    recent_notifications: [],
  };

  return (
    <SafeAreaView edges={['top']} style={styles.screen}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => {
          Alert.alert('Cerrar sesión', '¿Seguro que quieres salir?', [
            { text: 'Cancelar', style: 'cancel' },
            { text: 'Salir', style: 'destructive', onPress: async () => {
              await logout();
              router.replace('/(auth)/login');
            }},
          ]);
        }}>
          <Feather name="menu" size={22} color={colors.textDark} />
        </Pressable>
        <Text style={styles.headerTitle}>Proteg-rt</Text>
        <Pressable onPress={() => router.push('/(cobrador)/notificaciones' as any)}>
          <Ionicons name="notifications" size={24} color={colors.textDark} />
          {dashboard.recent_notifications.length > 0 && (
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{dashboard.recent_notifications.length}</Text>
            </View>
          )}
        </Pressable>
      </View>

      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={onRefresh} />}
      >
        {/* Saludo */}
        <View style={styles.greetingBox}>
          <Text style={typography.h1}>
            Buenos días, {dashboard.collector_name.split(' ')[0]} 👋
          </Text>
          <Text style={styles.dateText}>{formatDateFull(dashboard.date)}</Text>
        </View>

        {/* ── Tarjeta de Efectivo ── */}
        <Pressable style={styles.cashSection} onPress={() => router.push('/(cobrador)/efectivo')}>
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
              {formatMoney(dashboard.cash_pending)} <Text style={styles.cashCurrency}>MXN</Text>
            </Text>

            <View style={styles.progressRow}>
              <Text style={styles.progressLabel}>Progreso del límite</Text>
              <Text style={styles.progressPct}>{dashboard.cash_pct}%</Text>
            </View>
            <View style={styles.progressBg}>
              <LinearGradient
                colors={['#4CAF50', '#4A3AFF']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={[styles.progressFill, { width: `${Math.min(dashboard.cash_pct, 100)}%` }]}
              />
            </View>
            <Text style={styles.cashLimitText}>
              Tope: {formatMoney(dashboard.cash_limit || '5000.00')}
            </Text>
          </LinearGradient>
        </Pressable>

        {/* ── Resumen del Día ── */}
        <View style={styles.padded}>
          <SectionHeader title="Resumen del Día" />
          <View style={styles.statsGrid}>
            <StatCard
              icon="📋" iconBg={colors.primaryBg} iconColor={colors.primary}
              label="Cobros" value={String(dashboard.summary.collections_count)}
            />
            <StatCard
              icon="💵" iconBg={colors.successBg} iconColor={colors.success}
              label="Cobrado" value={formatMoney(dashboard.summary.collected_amount)}
            />
            <StatCard
              icon="🚩" iconBg={colors.orangeBg} iconColor={colors.orange}
              label="Pend. Aprob." value={String(dashboard.summary.pending_approval)}
            />
            <StatCard
              icon="💰" iconBg={colors.primaryBg} iconColor={colors.primary}
              label="Comisión Hoy" value={formatMoney(dashboard.summary.commission_today)}
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
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 20, paddingVertical: 14,
    backgroundColor: colors.white, borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  headerTitle: { fontSize: 20, fontWeight: '700', color: colors.primary, flex: 1, textAlign: 'center' },
  badge: {
    position: 'absolute', top: -4, right: -6, width: 18, height: 18, borderRadius: 9,
    backgroundColor: colors.badgeRed, justifyContent: 'center', alignItems: 'center',
  },
  badgeText: { fontSize: 10, fontWeight: '700', color: colors.white },
  scroll: { paddingBottom: 100 },
  greetingBox: { paddingHorizontal: 20, paddingTop: 24, paddingBottom: 16, backgroundColor: colors.white },
  dateText: { fontSize: 14, color: colors.textMedium, marginTop: 4 },
  cashSection: { paddingHorizontal: 20, marginTop: 16 },
  cashCard: { borderRadius: 20, paddingHorizontal: 24, paddingVertical: 24 },
  cashTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cashBadge: { backgroundColor: 'rgba(255,255,255,0.2)', paddingHorizontal: 14, paddingVertical: 6, borderRadius: 8 },
  cashBadgeText: { fontSize: 11, fontWeight: '700', color: colors.white, letterSpacing: 0.5 },
  cashChip: { backgroundColor: 'rgba(255,255,255,0.15)', paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12 },
  cashChipText: { fontSize: 12, fontWeight: '500', color: 'rgba(255,255,255,0.9)' },
  cashAmount: { fontSize: 42, fontWeight: '800', color: colors.white, marginTop: 16 },
  cashCurrency: { fontSize: 18, fontWeight: '500', color: 'rgba(255,255,255,0.7)' },
  progressRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 16 },
  progressLabel: { fontSize: 13, fontWeight: '500', color: 'rgba(255,255,255,0.8)' },
  progressPct: { fontSize: 13, fontWeight: '700', color: colors.white },
  progressBg: { marginTop: 8, height: 8, borderRadius: 4, backgroundColor: 'rgba(255,255,255,0.25)', overflow: 'hidden' },
  progressFill: { height: 8, borderRadius: 4 },
  cashLimitText: { marginTop: 8, fontSize: 12, fontWeight: '400', color: 'rgba(255,255,255,0.7)' },
  padded: { paddingHorizontal: 20 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
});
