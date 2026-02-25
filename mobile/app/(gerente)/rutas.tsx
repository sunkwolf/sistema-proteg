import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
} from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { colors, spacing } from '@/theme';
import { formatMoney } from '@/utils/format';

// ─── Mock ─────────────────────────────────────────────────────────────────────
type CobradorStatus = 'activo' | 'pausado' | 'sin_señal';

interface CobradorEnRuta {
  id: string;
  name: string;
  initials: string;
  zone: string;
  status: CobradorStatus;
  last_update: string;
  folios_visited: number;
  folios_total: number;
  collected: string;
  lat: number;
  lng: number;
}

const MOCK_COBRADORES: CobradorEnRuta[] = [
  { id: '1', name: 'Edgar Martínez', initials: 'EM', zone: 'Zona Norte', status: 'activo', last_update: 'Hace 2 min', folios_visited: 6, folios_total: 12, collected: '7200.00', lat: 20.628, lng: -103.234 },
  { id: '2', name: 'Laura Jiménez', initials: 'LJ', zone: 'Zona Centro', status: 'activo', last_update: 'Hace 5 min', folios_visited: 4, folios_total: 10, collected: '4800.00', lat: 20.621, lng: -103.241 },
  { id: '3', name: 'Carlos Vega', initials: 'CV', zone: 'Zona Sur', status: 'pausado', last_update: 'Hace 14 min', folios_visited: 8, folios_total: 11, collected: '9600.00', lat: 20.614, lng: -103.228 },
  { id: '4', name: 'Sofía Reyes', initials: 'SR', zone: 'Zona Oriente', status: 'sin_señal', last_update: 'Hace 31 min', folios_visited: 2, folios_total: 9, collected: '2400.00', lat: 20.635, lng: -103.219 },
];

const STATUS_CONFIG: Record<CobradorStatus, { label: string; color: string; bg: string; dot: string }> = {
  activo:    { label: 'Activo',     color: '#1B7A34', bg: '#DEF7E4', dot: '#34C759' },
  pausado:   { label: 'Pausado',    color: '#92600A', bg: '#FEF3C7', dot: '#F5A623' },
  sin_señal: { label: 'Sin señal',  color: '#636366', bg: '#F2F2F7', dot: '#AEAEB2' },
};

const AVATAR_COLORS = ['#4A3AFF', '#34C759', '#F5A623', '#FF3B30'];

// ─── Componente ───────────────────────────────────────────────────────────────
export default function RutasScreen() {
  const router = useRouter();
  const [selected, setSelected] = useState<string | null>(null);

  const activos = MOCK_COBRADORES.filter(c => c.status === 'activo').length;
  const pausados = MOCK_COBRADORES.filter(c => c.status === 'pausado').length;
  const sinSenal = MOCK_COBRADORES.filter(c => c.status === 'sin_señal').length;
  const totalCobrado = MOCK_COBRADORES.reduce((s, c) => s + parseFloat(c.collected), 0);

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={{ width: 40 }}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <Text style={styles.headerTitle}>Rutas en Tiempo Real</Text>
        <View style={{ width: 40 }} />
      </View>

      {/* Summary strip */}
      <View style={styles.strip}>
        <View style={styles.stripItem}>
          <View style={[styles.stripDot, { backgroundColor: '#34C759' }]} />
          <Text style={styles.stripNum}>{activos}</Text>
          <Text style={styles.stripLabel}>Activos</Text>
        </View>
        <View style={styles.stripDivider} />
        <View style={styles.stripItem}>
          <View style={[styles.stripDot, { backgroundColor: '#F5A623' }]} />
          <Text style={styles.stripNum}>{pausados}</Text>
          <Text style={styles.stripLabel}>Pausados</Text>
        </View>
        <View style={styles.stripDivider} />
        <View style={styles.stripItem}>
          <View style={[styles.stripDot, { backgroundColor: '#AEAEB2' }]} />
          <Text style={styles.stripNum}>{sinSenal}</Text>
          <Text style={styles.stripLabel}>Sin señal</Text>
        </View>
        <View style={styles.stripDivider} />
        <View style={styles.stripItem}>
          <Text style={styles.stripNum}>{formatMoney(totalCobrado)}</Text>
          <Text style={styles.stripLabel}>Cobrado hoy</Text>
        </View>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scroll}>

        {/* Map placeholder */}
        <View style={styles.mapContainer}>
          {/* Mock cobrador pins */}
          {MOCK_COBRADORES.map((c, i) => (
            <Pressable
              key={c.id}
              style={[
                styles.mapPin,
                {
                  top: 40 + i * 38,
                  left: 40 + (i % 3) * 90,
                  backgroundColor: selected === c.id ? '#1A1A2E' : AVATAR_COLORS[i],
                  opacity: c.status === 'sin_señal' ? 0.4 : 1,
                },
              ]}
              onPress={() => setSelected(selected === c.id ? null : c.id)}
            >
              <Text style={styles.mapPinText}>{c.initials}</Text>
              {c.status === 'activo' && <View style={styles.mapPinPulse} />}
            </Pressable>
          ))}
          <View style={styles.mapOverlay}>
            <MaterialCommunityIcons name="map-marker-path" size={20} color="rgba(255,255,255,0.3)" />
            <Text style={styles.mapOverlayText}>Tonalá, Jalisco</Text>
          </View>
        </View>

        {/* Cobrador cards */}
        <Text style={styles.sectionTitle}>COBRADORES</Text>

        {MOCK_COBRADORES.map((c, i) => {
          const cfg = STATUS_CONFIG[c.status];
          const pct = Math.round((c.folios_visited / c.folios_total) * 100);
          const isSelected = selected === c.id;

          return (
            <Pressable
              key={c.id}
              style={[styles.cobradorCard, isSelected && styles.cobradorCardSelected]}
              onPress={() => setSelected(isSelected ? null : c.id)}
            >
              {/* Top row */}
              <View style={styles.cardTop}>
                <View style={[styles.avatar, { backgroundColor: AVATAR_COLORS[i] }]}>
                  <Text style={styles.avatarText}>{c.initials}</Text>
                </View>
                <View style={{ flex: 1, marginLeft: 12 }}>
                  <Text style={styles.cobradorName}>{c.name}</Text>
                  <Text style={styles.cobradorZone}>{c.zone}</Text>
                </View>
                <View style={[styles.statusBadge, { backgroundColor: cfg.bg }]}>
                  <View style={[styles.statusDot, { backgroundColor: cfg.dot }]} />
                  <Text style={[styles.statusText, { color: cfg.color }]}>{cfg.label}</Text>
                </View>
              </View>

              {/* Progress */}
              <View style={styles.progressRow}>
                <Text style={styles.progressLabel}>
                  {c.folios_visited}/{c.folios_total} folios
                </Text>
                <Text style={styles.progressPct}>{pct}%</Text>
              </View>
              <View style={styles.progressTrack}>
                <View style={[styles.progressFill, { width: `${pct}%`, backgroundColor: AVATAR_COLORS[i] }]} />
              </View>

              {/* Bottom row */}
              <View style={styles.cardBottom}>
                <View style={styles.cardMetaItem}>
                  <Text style={styles.cardMetaLabel}>COBRADO</Text>
                  <Text style={styles.cardMetaValue}>{formatMoney(c.collected)}</Text>
                </View>
                <View style={styles.cardMetaItem}>
                  <Text style={styles.cardMetaLabel}>ÚLTIMA SEÑAL</Text>
                  <Text style={[styles.cardMetaValue, c.status === 'sin_señal' && { color: '#FF3B30' }]}>
                    {c.last_update}
                  </Text>
                </View>
                <Pressable
                  style={styles.histBtn}
                  onPress={() => router.push({
                    pathname: '/(gerente)/historial-ruta',
                    params: { cobrador_id: c.id, name: c.name },
                  })}
                >
                  <Ionicons name="map-outline" size={14} color={colors.primary} />
                  <Text style={styles.histBtnText}>Historial</Text>
                </Pressable>
              </View>
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

  // Summary strip
  strip: {
    flexDirection: 'row',
    backgroundColor: 'rgba(0,0,0,0.2)',
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
  stripItem: { flex: 1, alignItems: 'center', gap: 2 },
  stripDot: { width: 8, height: 8, borderRadius: 4, marginBottom: 2 },
  stripNum: { fontSize: 16, fontWeight: '700', color: colors.white },
  stripLabel: { fontSize: 10, color: 'rgba(255,255,255,0.7)', fontWeight: '500' },
  stripDivider: { width: 1, backgroundColor: 'rgba(255,255,255,0.2)', marginHorizontal: 4 },

  scrollView: { flex: 1, backgroundColor: colors.background },
  scroll: { paddingBottom: 24 },

  // Map
  mapContainer: {
    height: 200,
    backgroundColor: '#E8F0FE',
    position: 'relative',
    overflow: 'hidden',
  },
  mapPin: {
    position: 'absolute',
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: colors.white,
  },
  mapPinText: { fontSize: 11, fontWeight: '700', color: colors.white },
  mapPinPulse: {
    position: 'absolute',
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 2,
    borderColor: '#34C759',
    opacity: 0.4,
  },
  mapOverlay: {
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
  mapOverlayText: { fontSize: 11, color: colors.white },

  // Section
  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: colors.textMedium,
    letterSpacing: 0.8,
    paddingHorizontal: 16,
    paddingTop: 20,
    paddingBottom: 10,
  },

  // Cobrador card
  cobradorCard: {
    backgroundColor: colors.white,
    borderRadius: 14,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 6,
    elevation: 2,
  },
  cobradorCardSelected: {
    borderWidth: 2,
    borderColor: colors.primary,
  },
  cardTop: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: { fontSize: 14, fontWeight: '700', color: colors.white },
  cobradorName: { fontSize: 15, fontWeight: '700', color: colors.textDark },
  cobradorZone: { fontSize: 12, color: colors.textMedium, marginTop: 1 },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    gap: 5,
  },
  statusDot: { width: 7, height: 7, borderRadius: 3.5 },
  statusText: { fontSize: 12, fontWeight: '600' },

  progressRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  progressLabel: { fontSize: 12, color: colors.textMedium },
  progressPct: { fontSize: 12, fontWeight: '700', color: colors.textDark },
  progressTrack: {
    height: 6,
    backgroundColor: '#F0F0F5',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 12,
  },
  progressFill: { height: '100%', borderRadius: 3 },

  cardBottom: { flexDirection: 'row', alignItems: 'center' },
  cardMetaItem: { flex: 1 },
  cardMetaLabel: { fontSize: 10, fontWeight: '700', color: colors.textMedium, letterSpacing: 0.5 },
  cardMetaValue: { fontSize: 13, fontWeight: '600', color: colors.textDark, marginTop: 2 },
  histBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    borderWidth: 1,
    borderColor: colors.primary,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
  },
  histBtnText: { fontSize: 12, fontWeight: '600', color: colors.primary },
});
