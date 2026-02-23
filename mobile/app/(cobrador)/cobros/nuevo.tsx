import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  Pressable,
  TextInput,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import * as Location from 'expo-location';
import * as ImagePicker from 'expo-image-picker';
import { colors, spacing } from '@/theme';
import { formatMoney } from '@/utils/format';
import { PaymentMethod } from '@/types';

const MOCK = {
  folio: '18405',
  client: 'María López',
  payment_number: 3,
  total_payments: 7,
  expected: '1200.00',
  on_time: true,
};

const METHODS: { key: PaymentMethod; icon: string; label: string }[] = [
  { key: 'efectivo', icon: '💵', label: 'EFECTIVO' },
  { key: 'deposito', icon: '🏦', label: 'DEPÓSITO' },
  { key: 'transferencia', icon: '📱', label: 'TRANSFER.' },
];

export default function NuevoCobro() {
  const { folio } = useLocalSearchParams<{ folio: string }>();
  const router = useRouter();

  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState<PaymentMethod>('efectivo');
  const [receiptNumber, setReceiptNumber] = useState('');
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [gpsLocation, setGpsLocation] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const progressPct = ((MOCK.payment_number - 1) / MOCK.total_payments) * 100;

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') return Alert.alert('Permisos', 'Se necesita acceso a la cámara');
    const result = await ImagePicker.launchCameraAsync({ quality: 0.7 });
    if (!result.canceled && result.assets[0]) setPhotoUri(result.assets[0].uri);
  };

  const handleSubmit = async () => {
    if (!amount || !receiptNumber) {
      return Alert.alert('Campos requeridos', 'Completa monto y número de recibo');
    }
    setLoading(true);
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        const loc = await Location.getCurrentPositionAsync({});
        setGpsLocation('Tonalá, Jalisco');
      }
      // TODO: createProposal API call
      Alert.alert(
        '✅ Propuesta enviada',
        `F: ${folio} · ${formatMoney(amount)} · ${method}\n\nRecibirás notificación cuando sea aprobada.`,
        [
          { text: 'Ver propuestas', onPress: () => router.push('/(cobrador)/propuestas') },
          { text: 'Siguiente folio →', onPress: () => router.back() },
        ]
      );
    } catch (err: any) {
      Alert.alert('Error', err.message || 'No se pudo enviar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={{ width: 40 }}>
          <Text style={styles.backArrow}>←</Text>
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.headerTitle}>Registrar Cobro</Text>
          <Text style={styles.headerSub}>F: {MOCK.folio} · {MOCK.client}</Text>
        </View>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scroll}>
        {/* Progress card */}
        <View style={styles.progressCard}>
          <View style={styles.progressHeader}>
            <View>
              <Text style={styles.paymentSeq}>Pago #{MOCK.payment_number} de {MOCK.total_payments}</Text>
              <Text style={styles.expectedLabel}>Monto esperado</Text>
              <Text style={styles.expectedAmount}>{formatMoney(MOCK.expected)}</Text>
            </View>
            <View style={{ alignItems: 'flex-end' }}>
              <View style={[styles.timeBadge, { borderColor: MOCK.on_time ? '#34C759' : '#FF3B30' }]}>
                <Text style={[styles.timeBadgeText, { color: MOCK.on_time ? '#34C759' : '#FF3B30' }]}>
                  {MOCK.on_time ? 'En tiempo' : 'Vencido'}
                </Text>
              </View>
            </View>
          </View>
          <View style={styles.progressTrack}>
            <View style={[styles.progressFill, { width: `${progressPct}%` }]} />
          </View>
        </View>

        {/* Monto cobrado */}
        <Text style={styles.fieldLabel}>MONTO COBRADO</Text>
        <View style={styles.amountInput}>
          <Text style={styles.currencyPrefix}>$</Text>
          <TextInput
            style={styles.amountField}
            placeholder="0.00"
            placeholderTextColor="#B0B0BE"
            keyboardType="decimal-pad"
            value={amount}
            onChangeText={setAmount}
          />
        </View>

        {/* Método de pago */}
        <Text style={styles.fieldLabel}>MÉTODO DE PAGO</Text>
        <View style={styles.methodsRow}>
          {METHODS.map(m => (
            <Pressable
              key={m.key}
              style={[styles.methodCard, method === m.key && styles.methodCardActive]}
              onPress={() => setMethod(m.key)}
            >
              <Text style={{ fontSize: 20 }}>{m.icon}</Text>
              <Text style={[styles.methodText, method === m.key && { color: colors.primary }]}>{m.label}</Text>
            </Pressable>
          ))}
        </View>

        {/* Número de recibo */}
        <Text style={styles.fieldLabel}>NÚMERO DE RECIBO</Text>
        <View style={styles.receiptRow}>
          <View style={styles.receiptInput}>
            <TextInput
              style={styles.receiptField}
              placeholder="Recibo #"
              placeholderTextColor="#B0B0BE"
              value={receiptNumber}
              onChangeText={setReceiptNumber}
            />
          </View>
          <Pressable style={styles.scanBtn}>
            <Text style={{ fontSize: 20 }}>📷</Text>
          </Pressable>
        </View>

        {/* Tomar foto */}
        <Pressable style={styles.photoArea} onPress={takePhoto}>
          <View style={styles.photoLeft}>
            <Text style={{ fontSize: 24 }}>📸</Text>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.photoTitle}>
              {photoUri ? '✓ Foto adjunta' : 'Tomar Foto'}
            </Text>
            <Text style={styles.photoSub}>Opcional pero recomendado</Text>
          </View>
          <Text style={{ color: '#CCC', fontSize: 20 }}>›</Text>
        </Pressable>

        {/* GPS */}
        <View style={styles.gpsRow}>
          <Text style={{ fontSize: 14, marginRight: 6 }}>✅</Text>
          <Text style={styles.gpsText}>
            {gpsLocation || 'Tonalá, Jalisco'}
          </Text>
          <Text style={styles.gpsCaptured}>(Capturado)</Text>
        </View>

        <View style={{ height: 100 }} />
      </ScrollView>

      {/* Bottom */}
      <View style={styles.bottomBar}>
        <Pressable style={styles.submitBtn} onPress={handleSubmit}>
          <Text style={styles.submitText}>ENVIAR PROPUESTA</Text>
          <Text style={{ color: colors.white, fontSize: 16, marginLeft: 8 }}>➤</Text>
        </Pressable>
        <Text style={styles.disclaimer}>Quedará pendiente de autorización de gerencia</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.primary },

  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: colors.primary,
  },
  backArrow: { fontSize: 22, color: colors.white, fontWeight: '600' },
  headerTitle: { fontSize: 20, fontWeight: '700', color: colors.white },
  headerSub: { fontSize: 14, color: 'rgba(255,255,255,0.85)', marginTop: 2 },

  scrollView: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: 16 },

  // Progress card
  progressCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 20,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  paymentSeq: { fontSize: 13, color: '#8E8E93', marginBottom: 4 },
  expectedLabel: { fontSize: 12, color: '#8E8E93', marginBottom: 2 },
  expectedAmount: { fontSize: 24, fontWeight: '800', color: '#1A1A1A' },
  timeBadge: {
    borderWidth: 1.5,
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 4,
  },
  timeBadgeText: { fontSize: 12, fontWeight: '600' },
  progressTrack: {
    height: 8,
    backgroundColor: '#E8E8E8',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#34C759',
    borderRadius: 4,
  },

  // Fields
  fieldLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: '#555',
    letterSpacing: 0.5,
    marginBottom: 8,
    marginTop: 4,
  },

  amountInput: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    paddingHorizontal: 16,
    height: 56,
    marginBottom: 20,
  },
  currencyPrefix: { fontSize: 18, fontWeight: '600', color: '#1A1A1A', marginRight: 4 },
  amountField: { flex: 1, fontSize: 18, color: '#1A1A1A' },

  methodsRow: { flexDirection: 'row', gap: 10, marginBottom: 20 },
  methodCard: {
    flex: 1,
    alignItems: 'center',
    backgroundColor: colors.white,
    borderWidth: 1.5,
    borderColor: '#E5E5EA',
    borderRadius: 12,
    paddingVertical: 14,
    gap: 6,
  },
  methodCardActive: {
    borderColor: colors.primary,
    borderWidth: 2,
    backgroundColor: '#F8F7FF',
  },
  methodText: { fontSize: 11, fontWeight: '700', color: '#6C6C70', letterSpacing: 0.5 },

  receiptRow: { flexDirection: 'row', gap: 10, marginBottom: 20 },
  receiptInput: {
    flex: 1,
    backgroundColor: colors.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    paddingHorizontal: 16,
    height: 50,
    justifyContent: 'center',
  },
  receiptField: { fontSize: 15, color: '#1A1A1A' },
  scanBtn: {
    width: 50,
    height: 50,
    backgroundColor: colors.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    justifyContent: 'center',
    alignItems: 'center',
  },

  photoArea: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: '#B0B0E8',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  photoLeft: { marginRight: 12 },
  photoTitle: { fontSize: 15, fontWeight: '600', color: colors.primary },
  photoSub: { fontSize: 13, color: '#8E8E93', marginTop: 2 },

  gpsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  gpsText: { fontSize: 14, color: '#333', fontWeight: '500' },
  gpsCaptured: { fontSize: 13, color: '#34C759', fontWeight: '600', marginLeft: 6 },

  bottomBar: {
    backgroundColor: colors.background,
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 24,
  },
  submitBtn: {
    flexDirection: 'row',
    backgroundColor: colors.primary,
    borderRadius: 14,
    paddingVertical: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  submitText: { fontSize: 16, fontWeight: '700', color: colors.white, letterSpacing: 0.5 },
  disclaimer: { fontSize: 12, color: '#8E8E93', textAlign: 'center', marginTop: 8 },
});
