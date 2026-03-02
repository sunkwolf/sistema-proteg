import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Linking,
  Pressable,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { colors, spacing, typography } from '@/theme';
import { formatMoney, formatDateShort } from '@/utils/format';
import { useFolioDetail } from '@/hooks/useCollections';
import { FolioDetail } from '@/types';


export default function FolioDetailScreen() {
  const { folio } = useLocalSearchParams<{ folio: string }>();
  const router = useRouter();
  const { data, isLoading } = useFolioDetail(folio!);
  if (isLoading || !data) {
    return (
      <SafeAreaView edges={["top"]} style={styles.safe}>
        <View style={styles.header}>
          <Pressable onPress={() => router.back()} style={styles.backBtn}>
            <Ionicons name="chevron-back" size={24} color={colors.white} />
          </Pressable>
          <Text style={styles.headerTitle}>Cargando...</Text>
          <View style={{ width: 40 }} />
        </View>
      </SafeAreaView>
    );
  }
  const p = data.current_payment;
  const hasPriorPartials = parseFloat(p.partial_paid) > 0;

  const openPhone = () =>
    Linking.openURL(`tel:${data.client.phone.replace(/-/g, '')}`);

  const openMaps = () => {
    if (data.client.lat && data.client.lng) {
      Linking.openURL(
        `https://www.google.com/maps/dir/?api=1&destination=${data.client.lat},${data.client.lng}`
      );
    } else {
      Linking.openURL(
        `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(data.client.address)}`
      );
    }
  };

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* ── Header púrpura ── */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <Text style={styles.headerTitle}>Folio {data.folio}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scroll}
      >
        {/* ── Card Cliente ── */}
        <View style={styles.card}>
          <Text style={styles.sectionLabel}>CLIENTE</Text>
          <Text style={styles.clientName}>{data.client.name}</Text>

          <View style={styles.infoRow}>
            <Text style={styles.infoIcon}>📞</Text>
            <Text style={styles.infoText}>{data.client.phone}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoIcon}>📍</Text>
            <Text style={styles.infoText}>{data.client.address}</Text>
          </View>

          {/* Llamar / Navegar dentro de la card */}
          <View style={styles.clientActions}>
            <Pressable style={styles.clientActionBtn} onPress={openPhone}>
              <Text style={styles.clientActionIcon}>📞</Text>
              <Text style={styles.clientActionText}>Llamar</Text>
            </Pressable>
            <Pressable style={styles.clientActionBtn} onPress={openMaps}>
              <Text style={styles.clientActionIcon}>🧭</Text>
              <Text style={styles.clientActionText}>Navegar</Text>
            </Pressable>
          </View>
        </View>

        {/* ── Card Pago Pendiente ── */}
        <View style={styles.card}>
          <View style={styles.paymentHeader}>
            <View style={styles.paymentTitleRow}>
              <Text style={styles.alertIcon}>🔴</Text>
              <Text style={styles.paymentTitle}>PAGO PENDIENTE</Text>
            </View>
            {p.days_overdue > 0 && (
              <View style={styles.overdueBadge}>
                <Text style={styles.overdueBadgeText}>
                  {p.days_overdue} días de atraso
                </Text>
              </View>
            )}
          </View>

          <View style={styles.paymentBody}>
            <View style={styles.paymentLeft}>
              <Text style={styles.paymentSeq}>
                Pago #{p.number} de {p.total}
              </Text>
              <Text style={styles.paymentAmount}>
                {formatMoney(p.amount)}
              </Text>
            </View>
            <View style={styles.paymentRight}>
              <Text style={styles.dueDateLabel}>Fecha límite</Text>
              <Text style={styles.dueDateValue}>
                {formatDateShort(p.due_date)}
              </Text>
            </View>
          </View>

          {hasPriorPartials && (
            <View style={styles.partialBar}>
              <Text style={styles.partialText}>
                Abonado: {formatMoney(p.partial_paid)} · Resta:{' '}
                {formatMoney(p.partial_remaining)}
              </Text>
            </View>
          )}
        </View>

        {/* ── Card Vehículo Asegurado ── */}
        <View style={styles.card}>
          <View style={styles.vehicleTitleRow}>
            <Text style={styles.vehicleIcon}>🚗</Text>
            <Text style={styles.vehicleTitle}>VEHÍCULO ASEGURADO</Text>
          </View>
          <Text style={styles.vehicleDesc}>{data.vehicle.description}</Text>
          <Text style={styles.vehicleColor}>Color: {data.vehicle.color}</Text>
          <View style={styles.platesBadge}>
            <Text style={styles.platesText}>{data.vehicle.plates}</Text>
          </View>
        </View>

        {/* ── Botones de Acción ── */}
        <View style={styles.actions}>
          <Pressable
            style={styles.btnCobro}
            onPress={() =>
              router.push({
                pathname: '/(cobrador)/cobros/nuevo',
                params: { folio: folio! },
              })
            }
          >
            <Text style={styles.btnCobroIcon}>✅</Text>
            <Text style={styles.btnCobroText}>COBRO COMPLETO</Text>
          </Pressable>

          <Pressable
            style={styles.btnAbono}
            onPress={() =>
              router.push({
                pathname: '/(cobrador)/cobros/nuevo',
                params: { folio: folio!, type: 'partial' },
              })
            }
          >
            <Text style={styles.btnAbonoIcon}>💰</Text>
            <Text style={styles.btnAbonoText}>ABONO PARCIAL</Text>
          </Pressable>

          <Pressable
            style={styles.btnAviso}
            onPress={() =>
              router.push({
                pathname: '/(cobrador)/avisos/nuevo',
                params: { folio: folio! },
              })
            }
          >
            <Text style={styles.btnAvisoIcon}>📋</Text>
            <Text style={styles.btnAvisoText}>AVISO DE VISITA</Text>
          </Pressable>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.primary },
  // ── Header ──
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    height: 56,
  },
  backBtn: { width: 40, alignItems: 'flex-start' },
  backArrow: { fontSize: 22, color: colors.white, fontWeight: '600' },
  headerTitle: {
    ...typography.h3,
    color: colors.white,
    textAlign: 'center',
  },

  // ── Scroll ──
  scrollView: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: spacing.md, paddingBottom: 40 },

  // ── Card base ──
  card: {
    backgroundColor: colors.white,
    borderRadius: 16,
    padding: spacing.lg,
    marginBottom: spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },

  // ── Cliente ──
  sectionLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: colors.textMedium,
    letterSpacing: 1.2,
    marginBottom: spacing.xs,
  },
  clientName: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.textDark,
    marginBottom: spacing.sm,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  infoIcon: { fontSize: 16, marginRight: 8 },
  infoText: { fontSize: 15, color: colors.textDark },
  clientActions: {
    flexDirection: 'row',
    marginTop: spacing.md,
    gap: spacing.sm,
  },
  clientActionBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.background,
    borderRadius: 10,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: colors.border,
  },
  clientActionIcon: { fontSize: 14, marginRight: 6 },
  clientActionText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.primary,
  },

  // ── Pago Pendiente ──
  paymentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  paymentTitleRow: { flexDirection: 'row', alignItems: 'center' },
  alertIcon: { fontSize: 14, marginRight: 6 },
  paymentTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: colors.error,
    letterSpacing: 0.8,
  },
  overdueBadge: {
    backgroundColor: colors.errorBg,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  overdueBadgeText: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.error,
  },
  paymentBody: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },
  paymentLeft: { flex: 1 },
  paymentSeq: { fontSize: 13, color: colors.textMedium, marginBottom: 4 },
  paymentAmount: {
    fontSize: 28,
    fontWeight: '800',
    color: colors.textDark,
  },
  paymentRight: { alignItems: 'flex-end' },
  dueDateLabel: { fontSize: 12, color: colors.textMedium, marginBottom: 2 },
  dueDateValue: { fontSize: 16, fontWeight: '700', color: colors.textDark },
  partialBar: {
    marginTop: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  partialText: { fontSize: 13, color: colors.textMedium },

  // ── Vehículo ──
  vehicleTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  vehicleIcon: { fontSize: 16, marginRight: 6 },
  vehicleTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: colors.primary,
    letterSpacing: 0.8,
  },
  vehicleDesc: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textDark,
    marginBottom: 4,
  },
  vehicleColor: { fontSize: 14, color: colors.textMedium, marginBottom: 8 },
  platesBadge: {
    alignSelf: 'flex-start',
    backgroundColor: colors.background,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  platesText: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.textDark,
    letterSpacing: 1,
  },

  // ── Acciones ──
  actions: { marginTop: spacing.sm, gap: spacing.sm },
  btnCobro: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.success,
    borderRadius: 14,
    paddingVertical: 16,
  },
  btnCobroIcon: { fontSize: 18, marginRight: 8 },
  btnCobroText: { fontSize: 16, fontWeight: '700', color: colors.white },

  btnAbono: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.white,
    borderRadius: 14,
    paddingVertical: 16,
    borderWidth: 2,
    borderColor: colors.primary,
  },
  btnAbonoIcon: { fontSize: 18, marginRight: 8 },
  btnAbonoText: { fontSize: 16, fontWeight: '700', color: colors.primary },

  btnAviso: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 14,
    borderWidth: 1.5,
    borderColor: '#D0D0DC',
    backgroundColor: colors.white,
  },
  btnAvisoIcon: { fontSize: 16, marginRight: 6 },
  btnAvisoText: { fontSize: 15, fontWeight: '600', color: colors.textMedium },
});
