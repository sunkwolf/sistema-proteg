import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Linking,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { useLocalSearchParams, useRouter } from 'expo-router';
import { Card, Button } from '@/components/ui';
import { colors, spacing, typography } from '@/theme';
import { formatMoney, formatDateShort } from '@/utils/format';
import { FolioDetail } from '@/types';

// TODO: mock — reemplazar con fetch real
const MOCK_DETAIL: FolioDetail = {
  folio: '18405',
  client: {
    name: 'María López García',
    phone: '33-1234-5678',
    address: 'Av. Hidalgo 120, Tonalá, Jal.',
    lat: 20.6258,
    lng: -103.2350,
  },
  vehicle: {
    description: 'Toyota Corolla 2020',
    plates: 'ABC-123-D',
    color: 'Blanco',
  },
  policy: {
    coverage_type: 'AMPLIA',
    start_date: '2026-02-01',
    end_date: '2027-02-01',
    status: 'Activa',
  },
  current_payment: {
    number: 3,
    total: 7,
    amount: '1200.00',
    due_date: '2026-02-05',
    days_overdue: 18,
    partial_paid: '0.00',
    partial_remaining: '1200.00',
    partial_seq: 0,
  },
};

export default function FolioDetailScreen() {
  const { folio } = useLocalSearchParams<{ folio: string }>();
  const router = useRouter();
  const [data] = useState(MOCK_DETAIL);
  const p = data.current_payment;
  const hasPriorPartials = parseFloat(data.current_payment.partial_paid) > 0;

  const openPhone = () => Linking.openURL(`tel:${data.client.phone.replace(/-/g, '')}`);
  const openMaps = () => {
    if (data.client.lat && data.client.lng) {
      const url = `https://www.google.com/maps/dir/?api=1&destination=${data.client.lat},${data.client.lng}`;
      Linking.openURL(url);
    } else {
      const q = encodeURIComponent(data.client.address);
      Linking.openURL(`https://www.google.com/maps/search/?api=1&query=${q}`);
    }
  };

  return (

      <SafeAreaView edges={[]} style={styles.container}>
        <ScrollView contentContainerStyle={styles.scroll}>
          {/* Cliente */}
          <Card>
            <Text style={styles.sectionTitle}>CLIENTE</Text>
            <Text style={styles.clientName}>{data.client.name}</Text>
            <Text style={styles.detail}>📞 {data.client.phone}</Text>
            <Text style={styles.detail}>📍 {data.client.address}</Text>
          </Card>

          {/* Vehículo */}
          <Card>
            <Text style={styles.sectionTitle}>VEHÍCULO</Text>
            <Text style={styles.detail}>🚗 {data.vehicle.description}</Text>
            <Text style={styles.detail}>Placas: {data.vehicle.plates}</Text>
            <Text style={styles.detail}>Color: {data.vehicle.color}</Text>
          </Card>

          {/* Póliza */}
          <Card>
            <Text style={styles.sectionTitle}>PÓLIZA</Text>
            <Text style={styles.detail}>Cobertura: {data.policy.coverage_type}</Text>
            <Text style={styles.detail}>
              Vigencia: {formatDateShort(data.policy.start_date)} – {formatDateShort(data.policy.end_date)}
            </Text>
            <Text style={styles.detail}>
              Status: {data.policy.status} ✅
            </Text>
          </Card>

          {/* Pago pendiente */}
          <Card>
            <Text style={styles.sectionTitle}>PAGO PENDIENTE</Text>
            <Text style={styles.paymentInfo}>
              Pago #{p.number} de {p.total}
            </Text>
            <Text style={styles.paymentAmount}>
              Monto: {formatMoney(p.amount)}
            </Text>
            <Text style={styles.paymentDue}>
              Fecha límite: {formatDateShort(p.due_date)}
            </Text>
            {p.days_overdue > 0 && (
              <Text style={styles.overdue}>
                ⚠️ {p.days_overdue} días de atraso
              </Text>
            )}
            {hasPriorPartials && (
              <View style={styles.partialInfo}>
                <Text style={styles.detail}>
                  Abonado: {formatMoney(p.partial_paid)} · Pendiente: {formatMoney(p.partial_remaining)}
                </Text>
              </View>
            )}
          </Card>

          {/* Acciones */}
          <Text style={styles.sectionTitle}>ACCIONES</Text>

          <Button
            title="✅  COBRO COMPLETO"
            variant="success"
            size="lg"
            onPress={() => router.push({ pathname: '/(cobrador)/cobros/nuevo', params: { folio: folio! } })}
            style={{ marginBottom: spacing.md }}
          />

          <Button
            title="💰  ABONO PARCIAL"
            variant="secondary"
            size="lg"
            onPress={() => router.push({ pathname: '/(cobrador)/cobros/abono', params: { folio: folio! } })}
            style={{ marginBottom: spacing.md }}
          />

          <Button
            title="📋  AVISO DE VISITA"
            variant="ghost"
            size="lg"
            onPress={() => router.push({ pathname: '/(cobrador)/avisos/nuevo', params: { folio: folio! } })}
            style={{ marginBottom: spacing['2xl'] }}
          />

          <View style={styles.bottomActions}>
            <Button
              title="🗺️ Navegar"
              variant="secondary"
              size="sm"
              onPress={openMaps}
              style={{ flex: 1, marginRight: spacing.sm }}
            />
            <Button
              title="📞 Llamar"
              variant="secondary"
              size="sm"
              onPress={openPhone}
              style={{ flex: 1 }}
            />
          </View>
        </ScrollView>
      </SafeAreaView>

  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: spacing.lg, paddingBottom: 40 },
  sectionTitle: {
    ...typography.captionBold,
    color: colors.gray500,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: spacing.sm,
  },
  clientName: { ...typography.h3, color: colors.gray900, marginBottom: spacing.xs },
  detail: { ...typography.body, color: colors.gray700, marginBottom: 2 },
  paymentInfo: { ...typography.body, color: colors.gray700 },
  paymentAmount: { ...typography.moneySmall, color: colors.gray900, marginTop: spacing.xs },
  paymentDue: { ...typography.body, color: colors.gray600, marginTop: 2 },
  overdue: { ...typography.bodyBold, color: colors.danger, marginTop: spacing.sm },
  partialInfo: {
    marginTop: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.gray200,
  },
  bottomActions: {
    flexDirection: 'row',
    marginBottom: spacing.xl,
  },
});
