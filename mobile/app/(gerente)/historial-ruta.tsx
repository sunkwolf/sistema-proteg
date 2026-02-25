import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { colors } from '@/theme';
import { formatMoney } from '@/utils/format';

// ─── Mock ─────────────────────────────────────────────────────────────────────
interface VisitStop {
  time: string;
  hour: number;
  folio: string;
  client: string;
  address: string;
  result: 'cobrado' | 'abono' | 'aviso' | 'sin_respuesta';
  amount?: string;
}

const MOCK_VISITS: VisitStop[] = [
  { time: '08:12', hour: 8,  folio: '18405', client: 'María López',    address: 'Av. Hidalgo 120',     result: 'cobrado',       amount: '1200.00' },
  { time: '08:55', hour: 8,  folio: '18410', client: 'Juan Torres',    address: 'Calle Morelos 45',    result: 'sin_respuesta' },
  { time: '09:30', hour: 9,  folio: '18502', client: 'Ana González',   address: 'Blvd. Tonaltecas 88', result: 'abono',         amount: '500.00' },
  { time: '10:15', hour: 10, folio: '18510', client: 'Roberto Sánchez','address': 'Calle Juárez 12',   result: 'cobrado',       amount: '1401.00' },
  { time: '11:02', hour: 11, folio: '18615', client: 'Carmen Ruiz',    address: 'Av. Tlaquepaque 33',  result: 'aviso' },
  { time: '11:48', hour: 11, folio: '18620', client: 'Luis Mendoza',   address: 'Calle Reforma 67',    result: 'cobrado',       amount: '920.00' },
];

const RESULT_CONFIG = {
  cobrado:       { label: 'Cobrado',       color: '#1B7A34', bg: '#DEF7E4', icon: '✅' },
  abono:         { label: 'Abono',         color: '#92600A', bg: '#FEF3C7', icon: '💰' },
  aviso:         { label: 'Aviso',         color: '#3C3C43', bg: '#F0F0F5', icon: '📋' },
  sin_respuesta: { label: 'Sin respuesta', color: '#636366', bg: '#F2F2F7', icon: '🔕' },
};

const HOURS = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17];

// ─── Componente ───────────────────────────────────────────────────────────────
export default function HistorialRutaScreen() {
  const { name } = useLocalSearchParams<{ name: string }>();
  const router = useRouter();
  const [selectedHour, setSelectedHour] = useState<number | null>(null);

  const filteredVisits = selectedHour
    ? MOCK_VISITS.filter(v => v.hour === selectedHour)
    : MOCK_VISITS;

  const totalCobrado = MOCK_VISITS
    .filter(v => v.amount)
    .reduce((s, v) => s + parseFloat(v.amount!), 0);

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={{ width: 40 }}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.headerTitle}>Historial de Ruta</Text>
          <Text style={styles.headerSub}>{name || 'Cobrador'}</Text>
        </View>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scroll}>

        {/* Map placeholder */}
        <View style={styles.mapContainer}>
          {/* Route line mock */}
          <View style={styles.routeLine} />
          {MOCK_VISITS.map((v, i) => (
            <View
              key={v.folio}
              style={[
                styles.routePin,
                {
                  top: 30 + i * 25,
                  left: 50 + Math.sin(i * 1.2) * 60,
                  backgroundColor: RESULT_CONFIG[v.result].bg,
                  borderColor: v.result === 'cobrado' ? '#34C759'
                    : v.result === 'abono' ? '#F5A623'
                    : '#AEAEB2',
                },
              ]}
            >
              <Text style={{ fontSize: 10 }}>{RESULT_CONFIG[v.result].icon}</Text>
            </View>
          ))}
          <View style={styles.mapLabel}>
            <Ionicons name="time-outline" size={12} color="rgba(255,255,255,0.6)" />
            <Text style={styles.mapLabelText}>
              {selectedHour ? `${selectedHour}:00 — ${selectedHour + 1}:00` : 'Ruta completa del día'}
            </Text>
          </View>
        </View>

        {/* Stats strip */}
        <View style={styles.statsRow}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{MOCK_VISITS.length}</Text>
            <Text style={styles.statLabel}>Visitas</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statValue}>
              {MOCK_VISITS.filter(v => v.result === 'cobrado').length}
            </Text>
            <Text style={styles.statLabel}>Cobros</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{formatMoney(totalCobrado)}</Text>
            <Text style={styles.statLabel}>Total</Text>
          </View>
        </View>

        {/* Hour slider */}
        <Text style={styles.sectionTitle}>FILTRAR POR HORA</Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.hoursRow}
        >
          <Pressable
            style={[styles.hourChip, selectedHour === null && styles.hourChipActive]}
            onPress={() => setSelectedHour(null)}
          >
            <Text style={[styles.hourChipText, selectedHour === null && styles.hourChipTextActive]}>
              Todo
            </Text>
          </Pressable>
          {HOURS.map(h => {
            const hasVisit = MOCK_VISITS.some(v => v.hour === h);
            return (
              <Pressable
                key={h}
                style={[
                  styles.hourChip,
                  selectedHour === h && styles.hourChipActive,
                  !hasVisit && styles.hourChipEmpty,
                ]}
                onPress={() => setSelectedHour(selectedHour === h ? null : h)}
                disabled={!hasVisit}
              >
                <Text style={[
                  styles.hourChipText,
                  selectedHour === h && styles.hourChipTextActive,
                  !hasVisit && { color: '#CCCCD8' },
                ]}>
                  {h}:00
                </Text>
                {hasVisit && (
                  <View style={[
                    styles.hourDot,
                    { backgroundColor: selectedHour === h ? colors.white : colors.primary },
                  ]} />
                )}
              </Pressable>
            );
          })}
        </ScrollView>

        {/* Visit timeline */}
        <Text style={styles.sectionTitle}>
          {filteredVisits.length} VISITA{filteredVisits.length !== 1 ? 'S' : ''}
          {selectedHour ? ` A LAS ${selectedHour}:00` : ' EN TOTAL'}
        </Text>

        {filteredVisits.map((visit, i) => {
          const cfg = RESULT_CONFIG[visit.result];
          const isLast = i === filteredVisits.length - 1;
          return (
            <View key={visit.folio} style={styles.timelineItem}>
              {/* Time + line */}
              <View style={styles.timelineLeft}>
                <Text style={styles.timelineTime}>{visit.time}</Text>
                <View style={[styles.timelineDot, { backgroundColor: cfg.bg, borderColor: cfg.color === '#1B7A34' ? '#34C759' : cfg.color === '#92600A' ? '#F5A623' : '#AEAEB2' }]}>
                  <Text style={{ fontSize: 10 }}>{cfg.icon}</Text>
                </View>
                {!isLast && <View style={styles.timelineLine} />}
              </View>

              {/* Content */}
              <View style={styles.timelineContent}>
                <View style={styles.timelineHeader}>
                  <Text style={styles.timelineClient}>{visit.client}</Text>
                  <View style={[styles.resultBadge, { backgroundColor: cfg.bg }]}>
                    <Text style={[styles.resultText, { color: cfg.color }]}>{cfg.label}</Text>
                  </View>
                </View>
                <Text style={styles.timelineAddress}>
                  <Ionicons name="location-outline" size={11} color={colors.textMedium} /> {visit.address}
                </Text>
                <View style={styles.timelineBottom}>
                  <Text style={styles.timelineFolio}>F:{visit.folio}</Text>
                  {visit.amount && (
                    <Text style={styles.timelineAmount}>{formatMoney(visit.amount)}</Text>
                  )}
                </View>
              </View>
            </View>
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
  headerTitle: { fontSize: 20, fontWeight: '700', color: colors.white },
  headerSub: { fontSize: 13, color: 'rgba(255,255,255,0.8)', marginTop: 1 },

  scrollView: { flex: 1, backgroundColor: colors.background },
  scroll: { paddingBottom: 24 },

  // Map
  mapContainer: {
    height: 180,
    backgroundColor: '#E8F0FE',
    position: 'relative',
    overflow: 'hidden',
  },
  routeLine: {
    position: 'absolute',
    width: 2,
    height: '100%',
    backgroundColor: 'rgba(74,58,255,0.15)',
    left: 80,
  },
  routePin: {
    position: 'absolute',
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
  },
  mapLabel: {
    position: 'absolute',
    bottom: 10,
    right: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: 'rgba(0,0,0,0.35)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  mapLabelText: { fontSize: 11, color: colors.white },

  // Stats
  statsRow: {
    flexDirection: 'row',
    backgroundColor: colors.white,
    paddingVertical: 16,
  },
  statItem: { flex: 1, alignItems: 'center' },
  statValue: { fontSize: 18, fontWeight: '700', color: colors.textDark },
  statLabel: { fontSize: 11, color: colors.textMedium, marginTop: 2 },
  statDivider: { width: 1, backgroundColor: colors.border },

  // Hour slider
  sectionTitle: {
    fontSize: 11,
    fontWeight: '700',
    color: colors.textMedium,
    letterSpacing: 0.8,
    paddingHorizontal: 16,
    paddingTop: 20,
    paddingBottom: 10,
  },
  hoursRow: { paddingHorizontal: 16, gap: 8, paddingBottom: 4 },
  hourChip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
    minWidth: 56,
  },
  hourChipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  hourChipEmpty: { opacity: 0.4 },
  hourChipText: { fontSize: 13, fontWeight: '600', color: colors.textMedium },
  hourChipTextActive: { color: colors.white },
  hourDot: { width: 5, height: 5, borderRadius: 2.5, marginTop: 3 },

  // Timeline
  timelineItem: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 4,
  },
  timelineLeft: { width: 56, alignItems: 'center', paddingTop: 2 },
  timelineTime: { fontSize: 11, fontWeight: '600', color: colors.textMedium, marginBottom: 6 },
  timelineDot: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1.5,
    zIndex: 1,
  },
  timelineLine: { width: 2, flex: 1, backgroundColor: colors.border, marginTop: 4 },
  timelineContent: {
    flex: 1,
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 12,
    marginLeft: 10,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 4,
    elevation: 1,
  },
  timelineHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  timelineClient: { fontSize: 14, fontWeight: '700', color: colors.textDark, flex: 1 },
  resultBadge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6, marginLeft: 8 },
  resultText: { fontSize: 11, fontWeight: '700' },
  timelineAddress: { fontSize: 12, color: colors.textMedium, marginBottom: 8 },
  timelineBottom: { flexDirection: 'row', justifyContent: 'space-between' },
  timelineFolio: { fontSize: 12, color: colors.textMedium, fontWeight: '500' },
  timelineAmount: { fontSize: 14, fontWeight: '700', color: colors.primary },
});
