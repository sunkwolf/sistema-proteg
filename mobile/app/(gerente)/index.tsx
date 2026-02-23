import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Pressable,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { useAuthStore } from '@/store/auth';
import { Card, SectionHeader } from '@/components/ui';
import { colors, spacing, radius } from '@/theme';
import { formatMoney, formatDateFull } from '@/utils/format';

const CARD_W = (Dimensions.get('window').width - 40 - 12) / 2;

export default function DashboardGerente() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const router = useRouter();
  const [refreshing, setRefreshing] = React.useState(false);

  // TODO: useGerenteDashboard()
  const pending = 5;
  const stats = { approved: 28, amount: '33600.00', rejected: 3, corrected: 2 };
  const collectorsWithCash = 2;

  return (
    <SafeAreaView edges={['top']} style={styles.screen}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable><Text style={styles.hamburger}>☰</Text></Pressable>
        <Text style={styles.headerTitle}>Proteg · Cobranza</Text>
        <Pressable>
          <Text style={styles.bellIcon}>🔔</Text>
          <View style={styles.notifBadge}><Text style={styles.notifText}>{pending}</Text></View>
        </Pressable>
      </View>

      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => {
          setRefreshing(true); setTimeout(() => setRefreshing(false), 800);
        }} />}
      >
        {/* Greeting */}
        <Text style={styles.greeting}>Hola, {user?.name?.split(' ')[0] || 'Elena'} 👋</Text>
        <Text style={styles.date}>{formatDateFull(new Date().toISOString())}</Text>

        {/* Alert Banner */}
        {pending > 0 && (
          <Pressable
            style={styles.alertCard}
            onPress={() => router.push('/(gerente)/propuestas')}
          >
            <View style={styles.alertIcon}><Text style={{ fontSize: 24 }}>⏳</Text></View>
            <Text style={styles.alertTitle}>
              {pending} PENDIENTES{'\n'}
              <Text style={styles.alertSub}>de autorización</Text>
            </Text>
            <Text style={styles.alertDesc}>Solicitudes recientes requieren tu revisión</Text>
            <View style={styles.alertBtn}>
              <Text style={styles.alertBtnText}>Revisar ahora  →</Text>
            </View>
          </Pressable>
        )}

        {/* Stats */}
        <SectionHeader title="Resumen del Día" />
        <View style={styles.statsGrid}>
          <View style={[styles.statCard, { backgroundColor: colors.warningLight }]}>
            <View style={styles.statTop}>
              <Text style={styles.statLabel}>Aprobadas</Text>
              <View style={[styles.statIcon, { backgroundColor: colors.successLight }]}>
                <Text>✅</Text>
              </View>
            </View>
            <Text style={styles.statValue}>{stats.approved}</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: colors.warningLight }]}>
            <View style={styles.statTop}>
              <Text style={styles.statLabel}>Cobrado</Text>
              <View style={[styles.statIcon, { backgroundColor: colors.primaryBg }]}>
                <Text>💰</Text>
              </View>
            </View>
            <Text style={[styles.statValue, { fontSize: 28 }]}>{formatMoney(stats.amount)}</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: colors.dangerLight }]}>
            <View style={styles.statTop}>
              <Text style={styles.statLabel}>Rechazadas</Text>
              <View style={[styles.statIcon, { backgroundColor: colors.dangerLight }]}>
                <Text>❌</Text>
              </View>
            </View>
            <Text style={styles.statValue}>{stats.rejected}</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: colors.orangeBg }]}>
            <View style={styles.statTop}>
              <Text style={styles.statLabel}>Corregidas</Text>
              <View style={[styles.statIcon, { backgroundColor: colors.orangeBg }]}>
                <Text>🔧</Text>
              </View>
            </View>
            <Text style={styles.statValue}>{stats.corrected}</Text>
          </View>
        </View>

        {/* Cobradores con efectivo */}
        <Pressable
          style={styles.cobradorBanner}
          onPress={() => router.push('/(gerente)/efectivo')}
        >
          <View style={styles.cobradorIcon}><Text style={{ fontSize: 22 }}>💵</Text></View>
          <View style={{ flex: 1 }}>
            <Text style={styles.cobradorTitle}>Cobradores con efectivo pendiente</Text>
            <Text style={styles.cobradorSub}>
              Hay {collectorsWithCash} cobradores esperando confirmación
            </Text>
          </View>
          <Text style={styles.confirmLink}>Confirmar →</Text>
        </Pressable>

        {/* Quick Actions */}
        <View style={styles.actionsRow}>
          <Pressable
            style={styles.actionBtn}
            onPress={() => router.push('/(gerente)/propuestas')}
          >
            <Text style={{ fontSize: 28, marginBottom: 8 }}>📋</Text>
            <Text style={styles.actionLabel}>Propuestas</Text>
          </Pressable>
          <Pressable
            style={styles.actionBtn}
            onPress={() => router.push('/(gerente)/efectivo')}
          >
            <Text style={{ fontSize: 28, marginBottom: 8 }}>💵</Text>
            <Text style={styles.actionLabel}>Confirmar{'\n'}Efectivo</Text>
          </Pressable>
        </View>

        <Pressable onPress={logout} style={styles.logoutBtn}>
          <Text style={styles.logoutText}>Cerrar sesión</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 20, paddingVertical: 14, backgroundColor: colors.white,
    borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  hamburger: { fontSize: 22, color: colors.textDark },
  headerTitle: { fontSize: 18, fontWeight: '700', color: colors.textDark },
  bellIcon: { fontSize: 22 },
  notifBadge: {
    position: 'absolute', top: -4, right: -6, width: 18, height: 18, borderRadius: 9,
    backgroundColor: colors.error, justifyContent: 'center', alignItems: 'center',
  },
  notifText: { fontSize: 10, fontWeight: '700', color: colors.white },
  scroll: { paddingBottom: 100 },
  greeting: { fontSize: 32, fontWeight: '700', color: colors.textDark, paddingHorizontal: 20, paddingTop: 24 },
  date: { fontSize: 16, color: colors.textLight, paddingHorizontal: 20, marginTop: 4 },

  // Alert
  alertCard: {
    marginHorizontal: 20, marginTop: 20, backgroundColor: colors.warningLight,
    borderRadius: 16, padding: 24,
  },
  alertIcon: {
    width: 48, height: 48, borderRadius: 24, backgroundColor: colors.orange,
    justifyContent: 'center', alignItems: 'center', marginBottom: 12,
  },
  alertTitle: { fontSize: 18, fontWeight: '700', color: colors.textDark, marginBottom: 8 },
  alertSub: { fontWeight: '700' },
  alertDesc: { fontSize: 14, color: colors.gray500, marginBottom: 20 },
  alertBtn: {
    alignSelf: 'flex-start', backgroundColor: colors.warning, borderRadius: 12,
    paddingVertical: 14, paddingHorizontal: 24,
  },
  alertBtnText: { fontSize: 16, fontWeight: '700', color: colors.white },

  // Stats
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, paddingHorizontal: 20 },
  statCard: { width: CARD_W, borderRadius: 16, padding: 20, minHeight: 120 },
  statTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  statLabel: { fontSize: 15, fontWeight: '500', color: colors.gray500 },
  statIcon: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center' },
  statValue: { fontSize: 36, fontWeight: '700', color: colors.textDark },

  // Cobrador banner
  cobradorBanner: {
    marginHorizontal: 20, marginTop: 24, backgroundColor: colors.background,
    borderRadius: 16, padding: 20, flexDirection: 'row', alignItems: 'center',
  },
  cobradorIcon: {
    width: 44, height: 44, borderRadius: 22, backgroundColor: colors.primaryBg,
    justifyContent: 'center', alignItems: 'center', marginRight: 12,
  },
  cobradorTitle: { fontSize: 16, fontWeight: '700', color: colors.textDark },
  cobradorSub: { fontSize: 13, color: colors.textLight, marginTop: 2 },
  confirmLink: { fontSize: 15, fontWeight: '600', color: colors.primary },

  // Actions
  actionsRow: { flexDirection: 'row', paddingHorizontal: 20, marginTop: 24, gap: 12 },
  actionBtn: {
    flex: 1, backgroundColor: colors.primary, borderRadius: 16,
    paddingVertical: 24, alignItems: 'center',
  },
  actionLabel: { fontSize: 14, fontWeight: '600', color: colors.white, textAlign: 'center' },

  logoutBtn: { alignItems: 'center', marginTop: 32, padding: 16 },
  logoutText: { fontSize: 15, color: colors.textLight },
});
