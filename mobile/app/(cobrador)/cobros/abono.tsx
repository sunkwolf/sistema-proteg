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
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { colors, spacing } from '@/theme';
import { formatMoney } from '@/utils/format';

const MOCK = {
  folio: '18405',
  payment_number: 3,
  total: '1200.00',
  paid: '500.00',
  remaining: '700.00',
  abono_seq: 2,
  status: 'Activo',
};

type PaymentMethod = 'efectivo' | 'deposito' | 'transferencia';

export default function AbonoParcialScreen() {
  const { folio } = useLocalSearchParams<{ folio: string }>();
  const router = useRouter();
  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState<PaymentMethod>('efectivo');
  const [receipt, setReceipt] = useState('');

  const maxAmount = parseFloat(MOCK.remaining);
  const paidPct = (parseFloat(MOCK.paid) / parseFloat(MOCK.total)) * 100;

  const methods: { key: PaymentMethod; icon: string; label: string }[] = [
    { key: 'efectivo', icon: '💵', label: 'EFECTIVO' },
    { key: 'deposito', icon: '🏦', label: 'DEPÓSITO' },
    { key: 'transferencia', icon: '📱', label: 'TRANSFER.' },
  ];

  const handleSubmit = () => {
    const val = parseFloat(amount);
    if (!val || val <= 0) return Alert.alert('Error', 'Ingresa un monto válido');
    if (val > maxAmount) return Alert.alert('Error', `El monto máximo es ${formatMoney(MOCK.remaining)}`);
    if (!receipt.trim()) return Alert.alert('Error', 'Ingresa el número de recibo');
    router.replace({
      pathname: '/(cobrador)/cobros/exito',
      params: {
        folio: MOCK.folio,
        amount: amount,
        method: method,
        payment: String(MOCK.payment_number),
      },
    });
  };

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={{ width: 40 }}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.headerTitle}>Abono Parcial</Text>
          <Text style={styles.headerSub}>F: {MOCK.folio} · Pago #{MOCK.payment_number}</Text>
        </View>
        <Pressable style={{ width: 40, alignItems: 'flex-end' }}>
          <Text style={{ color: colors.white, fontSize: 20 }}>📋</Text>
        </Pressable>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scroll}>
        {/* Estado de Cuenta Card */}
        <View style={styles.accountCard}>
          <View style={styles.accountHeader}>
            <Text style={styles.accountTitle}>Estado de Cuenta</Text>
            <View style={styles.activeBadge}>
              <View style={styles.activeDot} />
              <Text style={styles.activeText}>{MOCK.status}</Text>
            </View>
          </View>

          <View style={styles.accountDivider} />

          <View style={styles.amountsRow}>
            <View>
              <Text style={styles.amountLabel}>Monto total</Text>
              <Text style={styles.amountValue}>{formatMoney(MOCK.total)}</Text>
            </View>
            <View style={{ alignItems: 'flex-end' }}>
              <Text style={styles.amountLabel}>PENDIENTE</Text>
              <Text style={[styles.amountValue, { color: colors.primary }]}>{formatMoney(MOCK.remaining)}</Text>
            </View>
          </View>

          <View style={{ marginTop: 16 }}>
            <Text style={styles.amountLabel}>Ya abonado</Text>
            <View style={styles.paidRow}>
              <Text style={styles.paidAmount}>{formatMoney(MOCK.paid)}</Text>
              <View style={styles.seqBadge}>
                <Text style={styles.seqBadgeText}>Abono #{MOCK.abono_seq} completado</Text>
              </View>
            </View>
          </View>

          {/* Progress bar */}
          <View style={styles.progressTrack}>
            <View style={[styles.progressFill, { width: `${paidPct}%` }]} />
          </View>
        </View>

        {/* Monto a abonar */}
        <Text style={styles.fieldLabel}>Monto a abonar</Text>
        <View style={styles.amountInput}>
          <Text style={styles.currencyPrefix}>$</Text>
          <TextInput
            style={styles.amountInputField}
            placeholder="0.00"
            placeholderTextColor="#B0B0BE"
            keyboardType="decimal-pad"
            value={amount}
            onChangeText={setAmount}
          />
          <Text style={styles.currencySuffix}>MXN</Text>
        </View>
        <View style={styles.amountHintRow}>
          <Text style={styles.amountHint}>Ingrese monto parcial</Text>
          <Text style={[styles.amountHint, { color: colors.primary, fontWeight: '600' }]}>Max: {formatMoney(MOCK.remaining)}</Text>
        </View>

        {/* Método de pago */}
        <Text style={styles.fieldLabel}>Método de pago</Text>
        <View style={styles.methodsRow}>
          {methods.map(m => (
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

        {/* Número de folio / recibo */}
        <Text style={styles.fieldLabel}>Número de folio / recibo</Text>
        <View style={styles.receiptRow}>
          <View style={styles.receiptInput}>
            <Text style={styles.receiptHash}>#</Text>
            <TextInput
              style={styles.receiptField}
              placeholder="Ej. REF-88392"
              placeholderTextColor="#B0B0BE"
              value={receipt}
              onChangeText={setReceipt}
            />
          </View>
          <Pressable style={styles.scanBtn}>
            <Text style={{ fontSize: 20 }}>📷</Text>
          </Pressable>
        </View>

        {/* Foto comprobante */}
        <Pressable style={styles.photoArea}>
          <Text style={{ fontSize: 28 }}>📸</Text>
          <Text style={styles.photoText}>Adjuntar Comprobante (Foto)</Text>
        </Pressable>

        {/* Warning */}
        <View style={styles.warningCard}>
          <Text style={{ fontSize: 16, marginRight: 10 }}>⚠️</Text>
          <Text style={styles.warningText}>
            Un abono parcial no activa servicios de grúa/siniestros. Solo el pago completo activa la cobertura.
          </Text>
        </View>

        <View style={{ height: 100 }} />
      </ScrollView>

      {/* Bottom button */}
      <View style={styles.bottomBar}>
        <Pressable style={styles.submitBtn} onPress={handleSubmit}>
          <Text style={styles.submitText}>ENVIAR ABONO</Text>
          <Text style={{ fontSize: 16, color: colors.white, marginLeft: 8 }}>✔</Text>
        </Pressable>
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
  activeDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#34C759', marginRight: 6 },
  activeText: { fontSize: 13, color: '#34C759', fontWeight: '600' },
  accountDivider: { height: 1, backgroundColor: '#E5E5EA', marginVertical: 12 },
  amountsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  amountLabel: { fontSize: 12, color: '#8E8E93', marginBottom: 4 },
  amountValue: { fontSize: 22, fontWeight: '800', color: '#1A1A1A' },
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
    backgroundColor: colors.primary,
    borderRadius: 4,
  },

  // Fields
  fieldLabel: { fontSize: 14, color: '#3C3C43', fontWeight: '500', marginBottom: 8, marginTop: 4 },

  amountInput: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    paddingHorizontal: 16,
    height: 56,
  },
  currencyPrefix: { fontSize: 18, fontWeight: '600', color: '#1A1A1A', marginRight: 4 },
  amountInputField: { flex: 1, fontSize: 18, color: '#1A1A1A' },
  currencySuffix: { fontSize: 14, color: '#8E8E93', fontWeight: '500' },
  amountHintRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 6,
    marginBottom: 20,
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
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: '#B0B0E8',
    borderRadius: 16,
    backgroundColor: '#FAFAFF',
    paddingVertical: 32,
    alignItems: 'center',
    marginBottom: 16,
  },
  photoText: { fontSize: 14, color: colors.primary, fontWeight: '500', marginTop: 8 },

  warningCard: {
    flexDirection: 'row',
    backgroundColor: '#FEF3C7',
    borderRadius: 12,
    padding: 16,
    alignItems: 'flex-start',
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
    backgroundColor: colors.primary,
    borderRadius: 14,
    paddingVertical: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  submitText: { fontSize: 16, fontWeight: '700', color: colors.white, letterSpacing: 0.5 },
});
