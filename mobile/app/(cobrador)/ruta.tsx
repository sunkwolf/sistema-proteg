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
import { Card, Button } from '@/components/ui';
import { colors, spacing, typography, radius } from '@/theme';
import { formatDateFull } from '@/utils/format';
import { RouteStop } from '@/types';

// TODO: datos reales
const MOCK_STOPS: RouteStop[] = [
  { order: 1, folio: '18405', client_name: 'María L.', address: 'Av. Hidalgo 120', lat: 20.6258, lng: -103.2350, status: 'completed' },
  { order: 2, folio: '18502', client_name: 'Ana G.', address: 'Reforma 45', lat: 20.6300, lng: -103.2400, status: 'next' },
  { order: 3, folio: '18510', client_name: 'Roberto S.', address: 'Juárez 88', lat: 20.6350, lng: -103.2450, status: 'pending' },
  { order: 4, folio: '18615', client_name: 'Carmen R.', address: 'Independencia 200', lat: 20.6400, lng: -103.2500, status: 'pending' },
];

const statusIcon: Record<string, string> = {
  completed: '✅',
  next: '▶️',
  pending: '⏳',
};

export default function RutaScreen() {
  const router = useRouter();
  const [stops] = useState(MOCK_STOPS);

  const nextStop = stops.find(s => s.status === 'next');

  const startNavigation = () => {
    if (nextStop) {
      const url = `https://www.google.com/maps/dir/?api=1&destination=${nextStop.lat},${nextStop.lng}`;
      Linking.openURL(url);
    }
  };

  const notifyRoute = () => {
    Alert.alert(
      'Notificar Ruta',
      `Se enviará WhatsApp a ${stops.length} clientes de tu ruta:\n\n"Hoy pasaré a tu domicilio a recoger el pago de tu póliza."`,
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'ENVIAR A TODOS  ✓', onPress: () => {
          // TODO: enviar notificaciones
          Alert.alert('✅', 'Mensajes enviados');
        }},
      ]
    );
  };

  return (
    <SafeAreaView edges={[]} style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>{formatDateFull(new Date().toISOString())}</Text>
        <Text style={styles.count}>{stops.length} visitas programadas</Text>

        {/* Mapa placeholder */}
        <Card style={styles.mapPlaceholder}>
          <Text style={styles.mapText}>🗺️ Mapa</Text>
          <Text style={styles.mapSub}>
            (Integración con react-native-maps pendiente)
          </Text>
        </Card>

        {/* Paradas */}
        <Text style={styles.sectionTitle}>PARADAS</Text>
        {stops.map((stop) => (
          <Pressable
            key={stop.order}
            onPress={() => router.push(`/(cobrador)/folios/${stop.folio}`)}
          >
            <Card style={stop.status === 'next' ? styles.nextCard : undefined}>
              <View style={styles.stopRow}>
                <Text style={styles.stopOrder}>
                  {statusIcon[stop.status]} {stop.order}.
                </Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.stopName}>F:{stop.folio} · {stop.client_name}</Text>
                  <Text style={styles.stopAddress}>📍 {stop.address}</Text>
                </View>
              </View>
            </Card>
          </Pressable>
        ))}

        {/* Acciones */}
        <Button
          title="📲 NOTIFICAR RUTA"
          variant="secondary"
          size="lg"
          onPress={notifyRoute}
          style={{ marginTop: spacing.xl }}
        />
        <Button
          title="▶️ Iniciar navegación"
          variant="primary"
          size="lg"
          onPress={startNavigation}
          style={{ marginTop: spacing.md }}
        />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: spacing.lg, paddingBottom: 40 },
  title: { ...typography.h3, color: colors.gray900 },
  count: { ...typography.caption, color: colors.gray500, marginBottom: spacing.lg },
  mapPlaceholder: {
    height: 180,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.gray100,
  },
  mapText: { fontSize: 40 },
  mapSub: { ...typography.caption, color: colors.gray400, marginTop: spacing.sm },
  sectionTitle: {
    ...typography.captionBold,
    color: colors.gray500,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginTop: spacing.lg,
    marginBottom: spacing.md,
  },
  nextCard: {
    borderWidth: 2,
    borderColor: colors.primary,
  },
  stopRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.md },
  stopOrder: { ...typography.bodyBold, color: colors.gray600, width: 44 },
  stopName: { ...typography.bodyBold, color: colors.gray800 },
  stopAddress: { ...typography.caption, color: colors.gray500 },
});
