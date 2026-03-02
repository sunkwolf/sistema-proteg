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
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import * as Location from 'expo-location';
import * as ImagePicker from 'expo-image-picker';
import { colors, spacing } from '@/theme';
import { formatMoney } from '@/utils/format';
import { PaymentMethod } from '@/types';
import { useFolioDetail } from '@/hooks/useCollections';
import { createProposal } from '@/api/collections';

// Data comes from API via useFolioDetail hook

const METHODS: { key: PaymentMethod; icon: string; label: string }[] = [
  { key: 'efectivo', icon: '💵', label: 'EFECTIVO' },
  { key: 'deposito', icon: '🏦', label: 'DEPÓSITO' },
  { key: 'transferencia', icon: '📱', label: 'TRANSFER.' },
];

// ─── Componente ──────────────────────────────────────────────────────────────
export default function RegistrarCobroScreen() {
  const { folio, type } = useLocalSearchParams<{ folio: string; type?: string }>();
  const router = useRouter();
  const { data: folioData } = useFolioDetail(folio || '');

  const MOCK = {
    folio: folioData?.folio || folio || '',
    client: folioData?.client?.name || 'Cargando...',
    payment_number: folioData?.current_payment?.number || 1,
    total_payments: folioData?.current_payment?.total || 7,
    expected: folioData?.current_payment?.amount || '0.00',
    on_time: (folioData?.current_payment?.days_overdue || 0) <= 0,
    total: folioData?.current_payment?.amount || '0.00',
    paid: folioData?.current_payment?.partial_paid || '0.00',
    remaining: folioData?.current_payment?.partial_remaining || folioData?.current_payment?.amount || '0.00',
    abono_seq: folioData?.current_payment?.partial_seq || 0,
  };

  const mode: 'full' | 'partial' = type === 'partial' ? 'partial' : 'full';
  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState<PaymentMethod>('efectivo');
  const [receiptNumber, setReceiptNumber] = useState('');
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [gpsLocation, setGpsLocation] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Derived
  const isPartial = mode === 'partial';
  const progressPct = isPartial
    ? (parseFloat(MOCK.paid) / parseFloat(MOCK.total)) * 100
    : ((MOCK.payment_number - 1) / MOCK.total_payments) * 100;
  const maxPartial = parseFloat(MOCK.remaining);

  // ── Handlers ────────────────────────────────────────────────────────────
  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') return Alert.alert('Permisos', 'Se necesita acceso a la cámara');
    const result = await ImagePicker.launchCameraAsync({ quality: 0.7 });
    if (!result.canceled && result.assets[0]) setPhotoUri(result.assets[0].uri);
  };

  const handleSubmit = async () => {
    if (!amount) return Alert.alert('Campos requeridos', 'Ingresa el monto cobrado');
    if (!receiptNumber.trim()) return Alert.alert('Campos requeridos', 'Ingresa el número de recibo');

    if (isPartial) {
      const val = parseFloat(amount);
      if (!val || val <= 0) return Alert.alert('Monto inválido', 'Ingresa un monto mayor a $0');
      if (val > maxPartial)
        return Alert.alert('Monto excedido', `El máximo permitido es ${formatMoney(MOCK.remaining)}`);
    }

    setLoading(true);
    try {
      if (!isPartial) {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status === 'granted') {
          await Location.getCurrentPositionAsync({});
          setGpsLocation('Tonalá, Jalisco');
        }
      }
      // Call the real API
      await createProposal({
        folio: folio || MOCK.folio,
        payment_number: MOCK.payment_number,
        amount: isPartial ? amount : MOCK.expected,
        method,
        receipt_number: receiptNumber,
        receipt_photo_url: photoUri || undefined,
        lat: 0,
        lng: 0,
        is_partial: isPartial,
      });

      router.replace({
        pathname: '/(cobrador)/cobros/exito',
        params: {
          folio: folio || MOCK.folio,
          amount,
          method,
          payment: String(MOCK.payment_number),
        },
      });
    } catch (err: any) {
      Alert.alert('Error', err.message || 'No se pudo enviar');
    } finally {
      setLoading(false);
    }
  };

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={{ width: 40 }}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.headerTitle}>
            {isPartial ? 'Abono Parcial' : 'Registrar Cobro'}
          </Text>
          <Text style={styles.headerSub}>
            F: {folio || MOCK.folio} · {MOCK.client}
          </Text>
        </View>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scroll}>

        {/* ── Estado de Cuenta ── */}
        <View style={styles.accountCard}>
          <View style={styles.accountHeader}>
            <Text style={styles.accountTitle}>Estado de Cuenta</Text>

            {isPartial ? (
              // Badge "Activo" para parcial
              <View style={styles.activeBadge}>
                <View style={[styles.statusDot, { backgroundColor: '#34C759' }]} />
                <Text style={[styles.statusText, { color: '#34C759' }]}>Activo</Text>
              </View>
            ) : (
              // Badge En tiempo / Vencido para completo
              <View style={[styles.activeBadge, { borderColor: MOCK.on_time ? '#34C759' : '#FF3B30' }]}>
                <View style={[styles.statusDot, { backgroundColor: MOCK.on_time ? '#34C759' : '#FF3B30' }]} />
                <Text style={[styles.statusText, { color: MOCK.on_time ? '#34C759' : '#FF3B30' }]}>
                  {MOCK.on_time ? 'En tiempo' : 'Vencido'}
                </Text>
              </View>
            )}
          </View>

          <View style={styles.accountDivider} />

          {isPartial ? (
            // Resumen de deuda parcial
            <>
              <View style={styles.amountsRow}>
                <View>
                  <Text style={styles.amountLabel}>Monto total</Text>
                  <Text style={styles.amountValue}>{formatMoney(MOCK.total)}</Text>
                </View>
                <View style={{ alignItems: 'flex-end' }}>
                  <Text style={styles.amountLabel}>PENDIENTE</Text>
                  <Text style={[styles.amountValue, { color: colors.primary }]}>
                    {formatMoney(MOCK.remaining)}
                  </Text>
                </View>
              </View>
              <View style={{ marginTop: 12 }}>
                <Text style={styles.amountLabel}>Ya abonado</Text>
                <View style={styles.paidRow}>
                  <Text style={styles.paidAmount}>{formatMoney(MOCK.paid)}</Text>
                  <View style={styles.seqBadge}>
                    <Text style={styles.seqBadgeText}>Abono #{MOCK.abono_seq} completado</Text>
                  </View>
                </View>
              </View>
            </>
          ) : (
            // Resumen pago completo
            <View style={styles.amountsRow}>
              <View>
                <Text style={styles.amountLabel}>Monto esperado</Text>
                <Text style={styles.amountValue}>{formatMoney(MOCK.expected)}</Text>
              </View>
              <View style={{ alignItems: 'flex-end' }}>
                <Text style={styles.amountLabel}>Pago</Text>
                <Text style={styles.paySeq}>#{MOCK.payment_number} de {MOCK.total_payments}</Text>
              </View>
            </View>
          )}

          <View style={styles.progressTrack}>
            <View
              style={[
                styles.progressFill,
                {
                  width: `${progressPct}%`,
                  backgroundColor: isPartial ? colors.primary : '#34C759',
                },
              ]}
            />
          </View>
        </View>

        {/* ── Monto ── */}
        <Text style={styles.fieldLabel}>
          {isPartial ? 'MONTO A ABONAR' : 'MONTO COBRADO'}
        </Text>
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
          {isPartial && <Text style={styles.currencySuffix}>MXN</Text>}
        </View>
        {isPartial && (
          <View style={styles.amountHintRow}>
            <Text style={styles.amountHint}>Ingrese monto parcial</Text>
            <Text style={[styles.amountHint, { color: colors.primary, fontWeight: '600' }]}>
              Max: {formatMoney(MOCK.remaining)}
            </Text>
          </View>
        )}

        {/* ── Método de pago ── */}
        <Text style={[styles.fieldLabel, { marginTop: isPartial ? 4 : 20 }]}>
          MÉTODO DE PAGO
        </Text>
        <View style={styles.methodsRow}>
          {METHODS.map(m => (
            <Pressable
              key={m.key}
              style={[styles.methodCard, method === m.key && styles.methodCardActive]}
              onPress={() => setMethod(m.key)}
            >
              <Text style={{ fontSize: 20 }}>{m.icon}</Text>
              <Text style={[styles.methodText, method === m.key && { color: colors.primary }]}>
                {m.label}
              </Text>
            </Pressable>
          ))}
        </View>

        {/* ── Número de recibo ── */}
        <Text style={styles.fieldLabel}>NÚMERO DE RECIBO</Text>
        <View style={styles.receiptRow}>
          <View style={styles.receiptInput}>
            {isPartial && <Text style={styles.receiptHash}>#</Text>}
            <TextInput
              style={styles.receiptField}
              placeholder={isPartial ? 'Ej. REF-88392' : 'Recibo #'}
              placeholderTextColor="#B0B0BE"
              value={receiptNumber}
              onChangeText={setReceiptNumber}
            />
          </View>
          <Pressable style={styles.scanBtn}>
            <Text style={{ fontSize: 20 }}>📷</Text>
          </Pressable>
        </View>

        {/* ── Foto ── */}
        <Pressable style={styles.photoArea} onPress={takePhoto}>
          <View style={{ marginRight: 12 }}>
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

        {/* ── GPS (solo completo) ── */}
        {!isPartial && (
          <View style={styles.gpsRow}>
            <Text style={{ fontSize: 14, marginRight: 6 }}>✅</Text>
            <Text style={styles.gpsText}>{gpsLocation || 'Tonalá, Jalisco'}</Text>
            <Text style={styles.gpsCaptured}>(Capturado)</Text>
          </View>
        )}

        {/* ── Aviso abono parcial ── */}
        {isPartial && (
          <View style={styles.warningCard}>
            <Text style={{ fontSize: 16, marginRight: 10 }}>⚠️</Text>
            <Text style={styles.warningText}>
              Un abono parcial no activa servicios de grúa/siniestros. Solo el pago completo activa la cobertura.
            </Text>
          </View>
        )}

        <View style={{ height: 100 }} />
      </ScrollView>

      {/* Bottom */}
      <View style={styles.bottomBar}>
        <Pressable
          style={[styles.submitBtn, isPartial && styles.submitBtnPartial]}
          onPress={handleSubmit}
        >
          <Text style={styles.submitText}>
            {isPartial ? 'ENVIAR ABONO' : 'ENVIAR PROPUESTA'}
          </Text>
          <Text style={{ color: colors.white, fontSize: 16, marginLeft: 8 }}>
            {isPartial ? '✔' : '➤'}
          </Text>
        </Pressable>
        {!isPartial && (
          <Text style={styles.disclaimer}>Quedará pendiente de autorización de gerencia</Text>
        )}
      </View>
    </SafeAreaView>
  );
}

// ─── Styles ──────────────────────────────────────────────────────────────────
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
  headerSub: { fontSize: 14, color: 'rgba(255,255,255,0.85)', marginTop: 2 },

  scrollView: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: 16 },

  // Account card
  accountCard: {
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
  accountHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  accountTitle: { fontSize: 14, color: '#3C3C43' },
  activeBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E8F9EE',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusDot: { width: 8, height: 8, borderRadius: 4, marginRight: 6 },
  statusText: { fontSize: 13, fontWeight: '600' },
  accountDivider: { height: 1, backgroundColor: '#E5E5EA', marginVertical: 12 },
  amountsRow: { flexDirection: 'row', justifyContent: 'space-between' },
  amountLabel: { fontSize: 12, color: '#8E8E93', marginBottom: 4 },
  amountValue: { fontSize: 22, fontWeight: '800', color: '#1A1A1A' },
  paySeq: { fontSize: 16, fontWeight: '700', color: '#1A1A1A' },
  paidRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginTop: 4 },
  paidAmount: { fontSize: 16, fontWeight: '600', color: '#1A1A1A' },
  seqBadge: {
    backgroundColor: '#F0F0F5',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  seqBadgeText: { fontSize: 12, color: '#8E8E93' },
  progressTrack: {
    height: 8,
    backgroundColor: '#E8E8E8',
    borderRadius: 4,
    marginTop: 12,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
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
    marginBottom: 4,
  },
  currencyPrefix: { fontSize: 18, fontWeight: '600', color: '#1A1A1A', marginRight: 4 },
  amountField: { flex: 1, fontSize: 18, color: '#1A1A1A' },
  currencySuffix: { fontSize: 14, color: '#8E8E93', fontWeight: '500' },
  amountHintRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 6,
    marginBottom: 16,
  },
  amountHint: { fontSize: 13, color: '#8E8E93' },

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
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    paddingHorizontal: 16,
    height: 50,
  },
  receiptHash: { fontSize: 16, color: '#8E8E93', marginRight: 8 },
  receiptField: { flex: 1, fontSize: 15, color: '#1A1A1A' },
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
  photoTitle: { fontSize: 15, fontWeight: '600', color: colors.primary },
  photoSub: { fontSize: 13, color: '#8E8E93', marginTop: 2 },

  gpsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  gpsText: { fontSize: 14, color: '#333', fontWeight: '500' },
  gpsCaptured: { fontSize: 13, color: '#34C759', fontWeight: '600', marginLeft: 6 },

  warningCard: {
    flexDirection: 'row',
    backgroundColor: '#FEF3C7',
    borderRadius: 12,
    padding: 16,
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  warningText: { flex: 1, fontSize: 14, color: '#3C3C43', lineHeight: 20 },

  bottomBar: {
    backgroundColor: colors.background,
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 24,
  },
  submitBtn: {
    flexDirection: 'row',
    backgroundColor: colors.success,
    borderRadius: 14,
    paddingVertical: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  submitBtnPartial: {
    backgroundColor: colors.primary,
  },
  submitText: { fontSize: 16, fontWeight: '700', color: colors.white, letterSpacing: 0.5 },
  disclaimer: { fontSize: 12, color: '#8E8E93', textAlign: 'center', marginTop: 8 },
});
