import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { colors } from '@/theme';
import { formatMoney } from '@/utils/format';

const SCREEN_W = Dimensions.get('window').width;

// ─── Mock ─────────────────────────────────────────────────────────────────────
const META_SEMANAL = 50000;
const COBRADO_SEMANAL = 33600;
const COMISION_PCT = 0.03; // 3%

interface CobradorComision {
  id: string;
  name: string;
  initials: string;
  color: string;
  cobrado: number;
  meta: number;
  comision: number;
}

const COBRADORES: CobradorComision[] = [
  { id: '1', name: 'Edgar Martínez',  initials: 'EM', color: '#4A3AFF', cobrado: 13200, meta: 15000, comision: 396 },
  { id: '2', name: 'Laura Jiménez',   initials: 'LJ', color: '#34C759', cobrado: 11400, meta: 12000, comision: 342 },
  { id: '3', name: 'Carlos Vega',     initials: 'CV', color: '#F5A623', cobrado: 9000,  meta: 13000, comision: 270 },
  { id: '4', name: 'Sofía Reyes',     initials: 'SR', color: '#FF3B30', cobrado: 0,     meta: 10000, comision: 0 },
];

// Últimos 7 días
const WEEKLY_DATA = [
  { day: 'L',  amount: 8200 },
  { day: 'M',  amount: 11400 },
  { day: 'Mi', amount: 6800 },
  { day: 'J',  amount: 9600 },
  { day: 'V',  amount: 7400 },
  { day: 'S',  amount: 0 },
  { day: 'D',  amount: 0 },
];

const MAX_BAR = Math.max(...WEEKLY_DATA.map(d => d.amount), 1);
const TODAY_INDEX = 3; // Jueves

// ─── Componente ───────────────────────────────────────────────────────────────
export default function ComisionesScreen() {
  const router = useRouter();
  const [expanded, setExpanded] = useState<string | null>(null);

  const pctMeta = Math.min((COBRADO_SEMANAL / META_SEMANAL) * 100, 100);
  const totalComisiones = COBRADORES.reduce((s, c) => s + c.comision, 0);
  const metaRestante = META_SEMANAL - COBRADO_SEMANAL;

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={{ width: 40 }}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <Text style={styles.headerTitle}>Comisiones</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scroll}>

        {/* ── Termómetro de meta ── */}
        <View style={styles.metaCard}>
          <View style={styles.metaHeader}>
            <Text style={styles.metaTitle}>META SEMANAL</Text>
            <Text style={styles.metaPct}>{Math.round(pctMeta)}%</Text>
          </View>

          {/* Termómetro */}
          <View style={styles.thermContainer}>
            {/* Bulbo */}
            <View style={styles.thermBulb}>
              <View style={[styles.thermBulbFill, {
                backgroundColor: pctMeta >= 80 ? '#34C759' : pctMeta >= 50 ? '#F5A623' : '#FF3B30'
              }]} />
            </View>
            {/* Tubo */}
            <View style={styles.thermTube}>
              <View style={styles.thermTrack}>
                <View style={[styles.thermFill, {
                  height: `${pctMeta}%`,
                  backgroundColor: pctMeta >= 80 ? '#34C759' : pctMeta >= 50 ? '#F5A623' : '#FF3B30',
                }]} />
              </View>
              {/* Marcas */}
              {[25, 50, 75, 100].map(mark => (
                <View key={mark} style={[styles.thermMark, { bottom: `${mark}%` }]}>
                  <View style={styles.thermMarkLine} />
                  <Text style={styles.thermMarkText}>{mark}%</Text>
                </View>
              ))}
            </View>
          </View>

          {/* Amounts */}
          <View style={styles.metaAmounts}>
            <View style={styles.metaAmountItem}>
              <Text style={styles.metaAmountLabel}>COBRADO</Text>
              <Text style={[styles.metaAmountValue, { color: '#34C759' }]}>
                {formatMoney(COBRADO_SEMANAL)}
              </Text>
            </View>
            <View style={[styles.metaAmountDivider]} />
            <View style={styles.metaAmountItem}>
              <Text style={styles.metaAmountLabel}>META</Text>
              <Text style={styles.metaAmountValue}>{formatMoney(META_SEMANAL)}</Text>
            </View>
            <View style={styles.metaAmountDivider} />
            <View style={styles.metaAmountItem}>
              <Text style={styles.metaAmountLabel}>FALTA</Text>
              <Text style={[styles.metaAmountValue, { color: '#FF3B30' }]}>
                {formatMoney(metaRestante)}
              </Text>
            </View>
          </View>

          {/* Progress bar lineal (complemento al termómetro) */}
          <View style={styles.progressTrack}>
            <View style={[styles.progressFill, {
              width: `${pctMeta}%`,
              backgroundColor: pctMeta >= 80 ? '#34C759' : pctMeta >= 50 ? '#F5A623' : '#FF3B30',
            }]} />
            {/* Marker de meta */}
            <View style={[styles.progressMarker, { left: '100%' }]} />
          </View>
          <Text style={styles.metaCaption}>Semana actual · comisión total: {formatMoney(totalComisiones)}</Text>
        </View>

        {/* ── Gráfica semanal ── */}
        <View style={styles.chartCard}>
          <Text style={styles.sectionTitle}>ÚLTIMOS 7 DÍAS</Text>
          <View style={styles.chart}>
            {WEEKLY_DATA.map((d, i) => {
              const barH = MAX_BAR > 0 ? (d.amount / MAX_BAR) * 100 : 0;
              const isToday = i === TODAY_INDEX;
              return (
                <View key={d.day} style={styles.chartBar}>
                  {d.amount > 0 && (
                    <Text style={styles.chartAmount} numberOfLines={1}>
                      {d.amount >= 1000 ? `${(d.amount / 1000).toFixed(1)}k` : d.amount}
                    </Text>
                  )}
                  <View style={styles.chartBarTrack}>
                    <View style={[
                      styles.chartBarFill,
                      {
                        height: `${barH}%`,
                        backgroundColor: isToday ? colors.primary : d.amount > 0 ? '#B0C4FF' : '#F0F0F5',
                      },
                    ]} />
                  </View>
                  <Text style={[styles.chartDay, isToday && { color: colors.primary, fontWeight: '700' }]}>
                    {d.day}
                  </Text>
                  {isToday && <View style={styles.chartTodayDot} />}
                </View>
              );
            })}
          </View>
        </View>

        {/* ── Desglose por cobrador ── */}
        <Text style={styles.sectionLabel}>DESGLOSE POR COBRADOR</Text>

        {COBRADORES.map(c => {
          const pct = Math.min((c.cobrado / c.meta) * 100, 100);
          const isOpen = expanded === c.id;

          return (
            <Pressable
              key={c.id}
              style={styles.cobradorCard}
              onPress={() => setExpanded(isOpen ? null : c.id)}
            >
              {/* Header row */}
              <View style={styles.cobradorTop}>
                <View style={[styles.avatar, { backgroundColor: c.color }]}>
                  <Text style={styles.avatarText}>{c.initials}</Text>
                </View>
                <View style={{ flex: 1, marginLeft: 12 }}>
                  <Text style={styles.cobradorName}>{c.name}</Text>
                  <View style={styles.cobradorMiniBar}>
                    <View style={[styles.cobradorMiniFill, { width: `${pct}%`, backgroundColor: c.color }]} />
                  </View>
                </View>
                <View style={{ alignItems: 'flex-end', marginLeft: 8 }}>
                  <Text style={styles.cobradorComision}>{formatMoney(c.comision)}</Text>
                  <Text style={styles.cobradorPct}>{Math.round(pct)}% de meta</Text>
                </View>
                <Ionicons
                  name={isOpen ? 'chevron-up' : 'chevron-down'}
                  size={16}
                  color={colors.textMedium}
                  style={{ marginLeft: 8 }}
                />
              </View>

              {/* Expanded detail */}
              {isOpen && (
                <View style={styles.cobradorDetail}>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Cobrado</Text>
                    <Text style={[styles.detailValue, { color: c.color }]}>{formatMoney(c.cobrado)}</Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Meta</Text>
                    <Text style={styles.detailValue}>{formatMoney(c.meta)}</Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Comisión ({(COMISION_PCT * 100).toFixed(0)}%)</Text>
                    <Text style={[styles.detailValue, { color: colors.primary, fontWeight: '700' }]}>
                      {formatMoney(c.comision)}
                    </Text>
                  </View>
                  <View style={[styles.detailRow, { marginTop: 4 }]}>
                    <Text style={styles.detailLabel}>Falta para meta</Text>
                    <Text style={[styles.detailValue, { color: '#FF3B30' }]}>
                      {formatMoney(Math.max(c.meta - c.cobrado, 0))}
                    </Text>
                  </View>
                </View>
              )}
            </Pressable>
          );
        })}

        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────
const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.primary },

  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: colors.primary,
  },
  headerTitle: { fontSize: 20, fontWeight: '700', color: colors.white, flex: 1, textAlign: 'center' },

  scrollView: { flex: 1, backgroundColor: colors.background },
  scroll: { paddingBottom: 24 },

  // Meta card
  metaCard: {
    backgroundColor: colors.white,
    margin: 16,
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.07,
    shadowRadius: 10,
    elevation: 3,
  },
  metaHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  metaTitle: { fontSize: 12, fontWeight: '700', color: colors.textMedium, letterSpacing: 0.8 },
  metaPct: { fontSize: 28, fontWeight: '800', color: colors.textDark },

  // Thermometer
  thermContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    height: 120,
    marginBottom: 20,
  },
  thermBulb: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#F0F0F5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
    marginBottom: -2,
  },
  thermBulbFill: { width: 16, height: 16, borderRadius: 8 },
  thermTube: { flex: 1, height: '100%', position: 'relative', justifyContent: 'flex-end' },
  thermTrack: {
    height: '100%',
    backgroundColor: '#F0F0F5',
    borderRadius: 4,
    overflow: 'hidden',
    justifyContent: 'flex-end',
  },
  thermFill: { width: '100%', borderRadius: 4 },
  thermMark: { position: 'absolute', left: 0, right: 0, flexDirection: 'row', alignItems: 'center' },
  thermMarkLine: { flex: 1, height: 1, backgroundColor: 'rgba(0,0,0,0.08)' },
  thermMarkText: { fontSize: 9, color: '#AEAEB2', marginLeft: 6, width: 28 },

  // Amounts
  metaAmounts: { flexDirection: 'row', marginBottom: 16 },
  metaAmountItem: { flex: 1, alignItems: 'center' },
  metaAmountLabel: { fontSize: 10, fontWeight: '700', color: colors.textMedium, letterSpacing: 0.5 },
  metaAmountValue: { fontSize: 14, fontWeight: '700', color: colors.textDark, marginTop: 4 },
  metaAmountDivider: { width: 1, backgroundColor: colors.border },

  progressTrack: {
    height: 8,
    backgroundColor: '#F0F0F5',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 8,
    position: 'relative',
  },
  progressFill: { height: '100%', borderRadius: 4 },
  progressMarker: { position: 'absolute', top: -2, width: 2, height: 12, backgroundColor: '#1A1A1A' },
  metaCaption: { fontSize: 12, color: colors.textMedium, textAlign: 'center' },

  // Chart
  chartCard: {
    backgroundColor: colors.white,
    marginHorizontal: 16,
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: '700',
    color: colors.textMedium,
    letterSpacing: 0.8,
    marginBottom: 16,
  },
  chart: { flexDirection: 'row', alignItems: 'flex-end', height: 100, gap: 6 },
  chartBar: { flex: 1, alignItems: 'center' },
  chartAmount: { fontSize: 9, color: colors.textMedium, marginBottom: 4, fontWeight: '600' },
  chartBarTrack: { width: '100%', height: 80, justifyContent: 'flex-end' },
  chartBarFill: { width: '100%', borderRadius: 4 },
  chartDay: { fontSize: 11, color: colors.textMedium, marginTop: 4, fontWeight: '500' },
  chartTodayDot: { width: 4, height: 4, borderRadius: 2, backgroundColor: colors.primary, marginTop: 2 },

  // Cobrador breakdown
  sectionLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: colors.textMedium,
    letterSpacing: 0.8,
    paddingHorizontal: 16,
    marginBottom: 10,
  },
  cobradorCard: {
    backgroundColor: colors.white,
    borderRadius: 14,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 4,
    elevation: 1,
  },
  cobradorTop: { flexDirection: 'row', alignItems: 'center' },
  avatar: { width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center' },
  avatarText: { fontSize: 13, fontWeight: '700', color: colors.white },
  cobradorName: { fontSize: 14, fontWeight: '600', color: colors.textDark, marginBottom: 6 },
  cobradorMiniBar: {
    height: 4,
    backgroundColor: '#F0F0F5',
    borderRadius: 2,
    overflow: 'hidden',
  },
  cobradorMiniFill: { height: '100%', borderRadius: 2 },
  cobradorComision: { fontSize: 15, fontWeight: '700', color: colors.primary },
  cobradorPct: { fontSize: 11, color: colors.textMedium, marginTop: 2 },

  cobradorDetail: {
    marginTop: 14,
    paddingTop: 14,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    gap: 8,
  },
  detailRow: { flexDirection: 'row', justifyContent: 'space-between' },
  detailLabel: { fontSize: 13, color: colors.textMedium },
  detailValue: { fontSize: 13, fontWeight: '600', color: colors.textDark },
});
