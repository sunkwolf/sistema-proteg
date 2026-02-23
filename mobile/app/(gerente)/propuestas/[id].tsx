import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  Alert,
  TextInput,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ScreenHeader } from '@/components/ui';
import { colors } from '@/theme';
import { formatMoney } from '@/utils/format';

const MOCK = {
  id: '1047',
  cobrador: 'Edgar R.',
  time: '10:15 AM',
  folio: '18510',
  client: 'Roberto S.',
  vehicle: 'Toyota Rav4 22',
  coverage: 'AMPLIA',
  // Lo que registró
  amount_received: '1401.00',
  payment_number: 1,
  total_payments: 7,
  method: 'Efectivo',
  receipt_ref: 'A00147',
  receipt_photo: null as string | null,
  gps_location: 'Tonalá, Jal.',
  // Lo que espera la póliza
  amount_expected: '1401.00',
  receipt_valid: true,
};

export default function DetalleProppuestaScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectInput, setShowRejectInput] = useState(false);

  const amountsMatch = MOCK.amount_received === MOCK.amount_expected;

  const handleApprove = () => {
    Alert.alert('✅ Propuesta aprobada', `F:${MOCK.folio} — ${formatMoney(MOCK.amount_received)} aprobado.`, [
      { text: 'OK', onPress: () => router.back() },
    ]);
  };

  const handleCorrectApprove = () => {
    Alert.alert('Corregir y aprobar', 'Se aprobará con corrección de monto.', [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Confirmar', onPress: () => router.back() },
    ]);
  };

  const handleReject = () => {
    if (!showRejectInput) {
      setShowRejectInput(true);
      return;
    }
    if (!rejectReason.trim()) return Alert.alert('Error', 'Ingresa el motivo del rechazo');
    Alert.alert('Rechazar propuesta', `Motivo: ${rejectReason}`, [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Rechazar', style: 'destructive', onPress: () => router.back() },
    ]);
  };

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      <ScreenHeader
        title={`Propuesta #${MOCK.id}`}
        subtitle={`👤 ${MOCK.cobrador} · 🕐 ${MOCK.time}`}
        rightIcon="⋮"
      />

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scroll}>
        {/* Póliza card */}
        <View style={styles.card}>
          <View style={styles.policyHeader}>
            <Text style={styles.policyLabel}>PÓLIZA</Text>
            <View style={styles.coverageBadge}>
              <Text style={styles.coverageText}>{MOCK.coverage}</Text>
            </View>
          </View>
          <Text style={styles.policyFolio}>F:{MOCK.folio} {MOCK.client}</Text>
          <View style={styles.vehicleRow}>
            <Text style={{ fontSize: 14, marginRight: 6 }}>🚗</Text>
            <Text style={styles.vehicleText}>{MOCK.vehicle}</Text>
          </View>
        </View>

        {/* Comparativa de Pago */}
        <Text style={styles.sectionTitle}>Comparativa de Pago</Text>

        {/* Lo que registró */}
        <View style={styles.card}>
          <View style={styles.cardTitleRow}>
            <Text style={{ fontSize: 16, marginRight: 8 }}>📝</Text>
            <Text style={styles.cardTitleText}>LO QUE REGISTRÓ</Text>
          </View>

          <View style={styles.divider} />

          <View style={styles.rowBetween}>
            <View>
              <Text style={styles.labelSmall}>Monto Recibido</Text>
              <Text style={styles.bigAmount}>{formatMoney(MOCK.amount_received)}</Text>
            </View>
            <View style={styles.payBadge}>
              <Text style={styles.payBadgeText}>Pago #{MOCK.payment_number} de {MOCK.total_payments}</Text>
            </View>
          </View>

          <View style={styles.methodRow}>
            <Text style={{ fontSize: 14, marginRight: 6 }}>💵</Text>
            <Text style={styles.methodText}>{MOCK.method}</Text>
          </View>

          <View style={styles.divider} />

          <Text style={styles.labelSmall}>Recibo Referencia</Text>
          <Text style={styles.valueText}>{MOCK.receipt_ref}</Text>

          <View style={styles.divider} />

          {/* Receipt photo placeholder */}
          <View style={styles.photoGpsRow}>
            <View style={styles.photoPlaceholder}>
              <Text style={{ fontSize: 24, opacity: 0.3 }}>🖼️</Text>
            </View>
            <View style={{ marginLeft: 12 }}>
              <Text style={styles.labelSmall}>Ubicación GPS</Text>
              <View style={{ flexDirection: 'row', alignItems: 'center', marginTop: 2 }}>
                <Text style={{ fontSize: 14, color: colors.primary, marginRight: 4 }}>📍</Text>
                <Text style={styles.gpsText}>{MOCK.gps_location}</Text>
              </View>
            </View>
          </View>
        </View>

        {/* Lo que espera la póliza */}
        <View style={styles.card}>
          <View style={styles.cardTitleRow}>
            <Text style={{ fontSize: 16, marginRight: 8 }}>✅</Text>
            <Text style={styles.cardTitleText}>LO QUE ESPERA LA PÓLIZA</Text>
          </View>

          <View style={styles.divider} />

          <View style={styles.rowBetween}>
            <View>
              <Text style={styles.labelSmall}>Monto Esperado</Text>
              <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                <Text style={[styles.bigAmount, { color: '#22C55E' }]}>
                  {formatMoney(MOCK.amount_expected)}
                </Text>
                {amountsMatch && <Text style={{ fontSize: 18, marginLeft: 6 }}>✅</Text>}
              </View>
              <Text style={styles.subText}>Pago programado</Text>
            </View>
            <View style={styles.payBadge}>
              <Text style={styles.payBadgeText}>Pago #{MOCK.payment_number}</Text>
            </View>
          </View>

          <View style={styles.divider} />

          <Text style={styles.labelSmall}>Validación de Recibo</Text>
          <View style={{ flexDirection: 'row', alignItems: 'center', marginTop: 4 }}>
            <Text style={{ fontSize: 14, marginRight: 6 }}>{MOCK.receipt_valid ? '✅' : '❌'}</Text>
            <Text style={[styles.valueText, { color: MOCK.receipt_valid ? '#22C55E' : '#FF3B30' }]}>
              {MOCK.receipt_valid ? 'Válido' : 'Inválido'}
            </Text>
          </View>
        </View>

        {/* Reject reason input */}
        {showRejectInput && (
          <View style={styles.rejectInputCard}>
            <Text style={styles.labelSmall}>Motivo del rechazo *</Text>
            <TextInput
              style={styles.rejectInput}
              placeholder="Describe el motivo..."
              placeholderTextColor="#B0B0BE"
              value={rejectReason}
              onChangeText={setRejectReason}
              multiline
            />
          </View>
        )}

        <View style={{ height: 120 }} />
      </ScrollView>

      {/* Bottom action buttons */}
      <View style={styles.bottomBar}>
        <Pressable style={styles.btnApprove} onPress={handleApprove}>
          <Text style={{ fontSize: 16, marginRight: 8 }}>✅</Text>
          <Text style={styles.btnApproveText}>APROBAR</Text>
        </Pressable>

        <Pressable style={styles.btnCorrect} onPress={handleCorrectApprove}>
          <Text style={{ fontSize: 16, marginRight: 8 }}>🔧</Text>
          <Text style={styles.btnCorrectText}>CORREGIR Y APROBAR</Text>
        </Pressable>

        <Pressable style={styles.btnReject} onPress={handleReject}>
          <Text style={{ fontSize: 16, marginRight: 8 }}>❌</Text>
          <Text style={styles.btnRejectText}>RECHAZAR</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.primary },
  scrollView: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: 16 },

  // Cards
  card: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 1,
  },

  // Policy
  policyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  policyLabel: { fontSize: 11, fontWeight: '700', color: colors.primary, letterSpacing: 1 },
  coverageBadge: {
    borderWidth: 1.5,
    borderColor: colors.primary,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 3,
  },
  coverageText: { fontSize: 12, fontWeight: '700', color: colors.primary },
  policyFolio: { fontSize: 18, fontWeight: '700', color: '#1A1A1A', marginBottom: 6 },
  vehicleRow: { flexDirection: 'row', alignItems: 'center' },
  vehicleText: { fontSize: 14, color: '#666' },

  // Section
  sectionTitle: { fontSize: 20, fontWeight: '700', color: '#1A1A1A', marginBottom: 12, marginTop: 4 },

  // Card internals
  cardTitleRow: { flexDirection: 'row', alignItems: 'center' },
  cardTitleText: { fontSize: 13, fontWeight: '700', color: '#1A1A1A', letterSpacing: 0.5 },
  divider: { height: 1, backgroundColor: '#F0F0F5', marginVertical: 14 },
  rowBetween: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  labelSmall: { fontSize: 12, color: '#8E8E93', marginBottom: 2 },
  bigAmount: { fontSize: 26, fontWeight: '800', color: '#1A1A1A' },
  subText: { fontSize: 13, color: '#8E8E93', marginTop: 2 },
  valueText: { fontSize: 15, fontWeight: '600', color: '#1A1A1A' },
  payBadge: {
    backgroundColor: '#F0F0F5',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  payBadgeText: { fontSize: 12, color: '#666', fontWeight: '500' },
  methodRow: { flexDirection: 'row', alignItems: 'center', marginTop: 8 },
  methodText: { fontSize: 14, color: '#555' },

  // Photo + GPS
  photoGpsRow: { flexDirection: 'row', alignItems: 'center' },
  photoPlaceholder: {
    width: 64,
    height: 64,
    borderRadius: 8,
    backgroundColor: '#F0F0F5',
    justifyContent: 'center',
    alignItems: 'center',
  },
  gpsText: { fontSize: 14, fontWeight: '600', color: '#1A1A1A' },

  // Reject
  rejectInputCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#FF3B30',
  },
  rejectInput: {
    fontSize: 15,
    color: '#1A1A1A',
    marginTop: 8,
    minHeight: 60,
    textAlignVertical: 'top',
  },

  // Bottom
  bottomBar: {
    backgroundColor: colors.white,
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 24,
    borderTopWidth: 1,
    borderTopColor: '#F0F0F5',
    gap: 10,
  },
  btnApprove: {
    flexDirection: 'row',
    backgroundColor: '#22C55E',
    borderRadius: 14,
    paddingVertical: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  btnApproveText: { fontSize: 16, fontWeight: '700', color: colors.white },

  btnCorrect: {
    flexDirection: 'row',
    backgroundColor: colors.primary,
    borderRadius: 14,
    paddingVertical: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  btnCorrectText: { fontSize: 16, fontWeight: '700', color: colors.white },

  btnReject: {
    flexDirection: 'row',
    backgroundColor: colors.white,
    borderRadius: 14,
    paddingVertical: 16,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FF3B30',
  },
  btnRejectText: { fontSize: 16, fontWeight: '700', color: '#FF3B30' },
});
