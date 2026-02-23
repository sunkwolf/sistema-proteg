import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  Alert,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { colors, spacing } from '@/theme';
import { formatDateFull } from '@/utils/format';
import { RouteStop } from '@/types';

const MOCK_STOPS: RouteStop[] = [
  { order: 1, folio: '18405', client_name: 'María L.', address: 'Av. Hidalgo 120', lat: 20.6258, lng: -103.235, status: 'completed', time: '09:30 AM' },
  { order: 2, folio: '18502', client_name: 'Ana G.', address: 'Reforma 45, Centro', lat: 20.63, lng: -103.24, status: 'next', time: null },
  { order: 3, folio: '18510', client_name: 'Roberto S.', address: 'Juárez 88', lat: 20.635, lng: -103.245, status: 'pending', time: '10:30 AM' },
  { order: 4, folio: '18615', client_name: 'Carmen R.', address: 'Independencia 200', lat: 20.64, lng: -103.25, status: 'pending', time: '11:00 AM' },
];

export default function RutaScreen() {
  const router = useRouter();
  const [stops] = useState(MOCK_STOPS);
  const nextStop = stops.find(s => s.status === 'next');

  const startNavigation = () => {
    if (nextStop) {
      Linking.openURL(`https://www.google.com/maps/dir/?api=1&destination=${nextStop.lat},${nextStop.lng}`);
    }
  };

  const notifyRoute = () => {
    Alert.alert(
      'Notificar Ruta',
      `Se enviará WhatsApp a ${stops.length} clientes:\n\n"Hoy pasaré a tu domicilio a recoger el pago de tu póliza."`,
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Enviar', onPress: () => Alert.alert('✅', 'Mensajes enviados') },
      ]
    );
  };

  const renderStopIcon = (status: string, order: number) => {
    if (status === 'completed') {
      return (
        <View style={[styles.stopIconCircle, { backgroundColor: '#34C759' }]}>
          <Text style={styles.stopIconText}>✓</Text>
        </View>
      );
    }
    if (status === 'next') {
      return (
        <View style={[styles.stopIconCircle, { backgroundColor: colors.primary, width: 48, height: 48, borderRadius: 24 }]}>
          <Text style={styles.stopIconText}>▶</Text>
        </View>
      );
    }
    return (
      <View style={[styles.stopIconCircle, { backgroundColor: '#E5E5EA' }]}>
        <Text style={[styles.stopIconText, { color: '#6C6C70' }]}>{order}</Text>
      </View>
    );
  };

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.backArrow}>←</Text>
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.headerTitle}>Mi Ruta del Día</Text>
        </View>
        <Pressable style={{ width: 40, alignItems: 'flex-end' }}>
          <Text style={{ color: colors.white, fontSize: 20 }}>⋮</Text>
        </Pressable>
      </View>

      {/* Date bar */}
      <View style={styles.dateBar}>
        <Text style={styles.dateText}>📅 {formatDateFull(new Date().toISOString())}</Text>
        <View style={styles.visitsBadge}>
          <Text style={styles.visitsBadgeText}>{stops.length} visitas programadas</Text>
        </View>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scroll}>
        {/* Map placeholder */}
        <View style={styles.mapPlaceholder}>
          <View style={styles.mapInner}>
            <Text style={{ fontSize: 48, opacity: 0.3 }}>🗺️</Text>
            <Text style={styles.mapSubtext}>Mapa — react-native-maps pendiente</Text>
          </View>
        </View>

        {/* Drag handle */}
        <View style={styles.dragHandle} />

        {/* Stops list */}
        {stops.map((stop) => (
          <Pressable
            key={stop.order}
            onPress={() => router.push(`/(cobrador)/folios/${stop.folio}`)}
          >
            <View style={[
              styles.stopCard,
              stop.status === 'next' && styles.stopCardActive,
            ]}>
              {renderStopIcon(stop.status, stop.order)}
              <View style={styles.stopContent}>
                <View style={styles.stopTitleRow}>
                  <Text style={[
                    styles.stopName,
                    stop.status === 'next' && { fontSize: 17 },
                  ]}>
                    {stop.order}. F:{stop.folio} {stop.client_name}
                  </Text>
                  {stop.status === 'next' && (
                    <View style={styles.actualBadge}>
                      <Text style={styles.actualBadgeText}>ACTUAL</Text>
                    </View>
                  )}
                </View>
                <Text style={styles.stopAddress}>
                  {stop.status === 'next' ? '📍 ' : ''}{stop.address}
                  {stop.status === 'completed' ? ` • Visitado ${stop.time}` : ''}
                </Text>
              </View>
              <View style={styles.stopRight}>
                {stop.status === 'completed' && (
                  <Text style={{ color: '#34C759', fontSize: 13, fontWeight: '500' }}>Hecho</Text>
                )}
                {stop.status === 'next' && (
                  <Text style={{ color: colors.primary, fontSize: 20 }}>➤</Text>
                )}
                {stop.status === 'pending' && stop.time && (
                  <Text style={{ color: '#8E8E93', fontSize: 13 }}>{stop.time}</Text>
                )}
              </View>
            </View>
          </Pressable>
        ))}

        {/* Spacer for buttons */}
        <View style={{ height: 140 }} />
      </ScrollView>

      {/* Bottom action buttons */}
      <View style={styles.bottomActions}>
        <Pressable style={styles.btnNotify} onPress={notifyRoute}>
          <View style={{ alignItems: 'center' }}>
            <Text style={styles.btnNotifyText}>NOTIFICAR RUTA</Text>
            <Text style={styles.btnNotifySub}>Enviar aviso por WhatsApp</Text>
          </View>
        </Pressable>
        <Pressable style={styles.btnNavigate} onPress={startNavigation}>
          <Text style={styles.btnNavigateIcon}>▲</Text>
          <Text style={styles.btnNavigateText}>Iniciar navegación</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.primary },

  // Header
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: colors.primary,
  },
  backBtn: { width: 40 },
  backArrow: { fontSize: 22, color: colors.white, fontWeight: '600' },
  headerTitle: { fontSize: 20, fontWeight: '700', color: colors.white },

  // Date bar
  dateBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingBottom: 16,
    backgroundColor: colors.primary,
  },
  dateText: { fontSize: 14, color: 'rgba(255,255,255,0.85)' },
  visitsBadge: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 16,
  },
  visitsBadgeText: { fontSize: 12, color: colors.white, fontWeight: '500' },

  // Scroll
  scrollView: { flex: 1, backgroundColor: colors.background },
  scroll: { paddingBottom: 20 },

  // Map
  mapPlaceholder: {
    height: 200,
    backgroundColor: '#E8E8F0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  mapInner: { alignItems: 'center' },
  mapSubtext: { fontSize: 13, color: '#8E8E93', marginTop: 8 },

  // Drag handle
  dragHandle: {
    width: 40,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#C7C7CC',
    alignSelf: 'center',
    marginVertical: 12,
  },

  // Stop cards
  stopCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 10,
  },
  stopCardActive: {
    borderLeftWidth: 4,
    borderLeftColor: colors.primary,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 3,
  },
  stopIconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  stopIconText: { fontSize: 16, fontWeight: '700', color: colors.white },
  stopContent: { flex: 1 },
  stopTitleRow: { flexDirection: 'row', alignItems: 'center', flexWrap: 'wrap' },
  stopName: { fontSize: 15, fontWeight: '600', color: '#1C1C1E' },
  actualBadge: {
    backgroundColor: '#E8E7FB',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
    marginLeft: 8,
  },
  actualBadgeText: { fontSize: 10, fontWeight: '700', color: colors.primary, letterSpacing: 0.5 },
  stopAddress: { fontSize: 13, color: '#8E8E93', marginTop: 4 },
  stopRight: { marginLeft: 8, alignItems: 'flex-end' },

  // Bottom buttons
  bottomActions: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: colors.background,
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 24,
  },
  btnNotify: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    marginBottom: 10,
  },
  btnNotifyText: { fontSize: 15, fontWeight: '700', color: colors.white, letterSpacing: 0.5 },
  btnNotifySub: { fontSize: 12, color: 'rgba(255,255,255,0.7)', marginTop: 2 },
  btnNavigate: {
    flexDirection: 'row',
    backgroundColor: colors.white,
    borderWidth: 2,
    borderColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  btnNavigateIcon: { fontSize: 16, color: colors.primary, marginRight: 8 },
  btnNavigateText: { fontSize: 15, fontWeight: '600', color: colors.primary },
});
