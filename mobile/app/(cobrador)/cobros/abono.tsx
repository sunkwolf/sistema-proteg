import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  Pressable,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { useLocalSearchParams, useRouter } from 'expo-router';
import * as Location from 'expo-location';
import * as ImagePicker from 'expo-image-picker';
import { Card, Button, Input } from '@/components/ui';
import { colors, spacing, typography, radius } from '@/theme';
import { formatMoney } from '@/utils/format';
import { PaymentMethod } from '@/types';

const METHODS: { key: PaymentMethod; label: string }[] = [
  { key: 'efectivo', label: 'EFECTIVO' },
  { key: 'deposito', label: 'DEPÓSITO' },
  { key: 'transferencia', label: 'TRANSFERENCIA' },
];

export default function AbonoParcial() {
  const { folio } = useLocalSearchParams<{ folio: string }>();
  const router = useRouter();

  // TODO: datos reales del folio
  const totalAmount = '1200.00';
  const alreadyPaid = '500.00';
  const remaining = '700.00';
  const partialSeq = 2;

  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState<PaymentMethod | null>(null);
  const [receiptNumber, setReceiptNumber] = useState('');
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const amountNum = parseFloat(amount) || 0;
  const remainingNum = parseFloat(remaining);
  const completesPayment = amountNum > 0 && amountNum >= remainingNum;

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permisos', 'Se necesita acceso a la cámara');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({ quality: 0.7 });
    if (!result.canceled && result.assets[0]) {
      setPhotoUri(result.assets[0].uri);
    }
  };

  const handleSubmit = async () => {
    if (!amount || !method || !receiptNumber) {
      Alert.alert('Campos requeridos', 'Completa monto, método de pago y número de recibo');
      return;
    }
    if (amountNum > remainingNum) {
      Alert.alert('Error', `El abono no puede ser mayor al pendiente (${formatMoney(remaining)})`);
      return;
    }

    setLoading(true);
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      let lat = 0, lng = 0;
      if (status === 'granted') {
        const loc = await Location.getCurrentPositionAsync({});
        lat = loc.coords.latitude;
        lng = loc.coords.longitude;
      }

      // TODO: upload photo + createProposal (is_partial: true)

      Alert.alert(
        '✅ Abono enviado',
        `F: ${folio} · Abono ${formatMoney(amount)} · ${method}`,
        [
          { text: 'Ver mis propuestas', onPress: () => router.push('/(cobrador)/propuestas') },
          { text: 'Siguiente folio →', onPress: () => router.back() },
        ]
      );
    } catch (err: any) {
      Alert.alert('Error', err.message || 'No se pudo enviar el abono');
    } finally {
      setLoading(false);
    }
  };

  return (

      <SafeAreaView edges={[]} style={styles.container}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text style={styles.folioLabel}>F: {folio} · Pago #3</Text>

          {/* Estado del pago */}
          <Card>
            <Text style={styles.sectionTitle}>ESTADO DEL PAGO #3</Text>
            <Text style={styles.row}>Monto total: {formatMoney(totalAmount)}</Text>
            <Text style={styles.row}>Abonado: {formatMoney(alreadyPaid)}</Text>
            <Text style={[styles.row, styles.bold]}>Pendiente: {formatMoney(remaining)}</Text>
            <Text style={styles.row}>Abono #: {partialSeq}</Text>
          </Card>

          {/* Monto del abono */}
          <Input
            label="MONTO DEL ABONO *"
            placeholder="0.00"
            value={amount}
            onChangeText={setAmount}
            keyboardType="decimal-pad"
          />
          <Text style={styles.maxHint}>Max: {formatMoney(remaining)} (pendiente)</Text>

          {completesPayment && (
            <Card style={{ backgroundColor: colors.successLight }}>
              <Text style={{ color: colors.success, fontWeight: '600' }}>
                🎉 ¡Este abono completa el pago! Activará la cobertura.
              </Text>
            </Card>
          )}

          {/* Método de pago */}
          <Text style={styles.fieldLabel}>MÉTODO DE PAGO *</Text>
          <View style={styles.methodRow}>
            {METHODS.map((m) => (
              <Pressable
                key={m.key}
                onPress={() => setMethod(m.key)}
                style={[styles.methodChip, method === m.key && styles.methodChipActive]}
              >
                <Text style={[styles.methodText, method === m.key && styles.methodTextActive]}>
                  {m.label}
                </Text>
              </Pressable>
            ))}
          </View>

          {/* Recibo */}
          <Input
            label="NÚMERO DE RECIBO *"
            placeholder="Recibo #"
            value={receiptNumber}
            onChangeText={setReceiptNumber}
          />

          {/* Foto */}
          <Text style={styles.fieldLabel}>FOTO RECIBO (Opcional)</Text>
          <Pressable style={styles.photoBtn} onPress={takePhoto}>
            <Text style={styles.photoBtnText}>
              {photoUri ? '✓ Foto adjunta' : '📷 Tomar foto'}
            </Text>
          </Pressable>

          {/* Aviso */}
          <Card style={{ backgroundColor: colors.warningLight }}>
            <Text style={{ ...typography.caption, color: colors.warning }}>
              ⚠️ Un abono parcial no activa servicios de grúa/siniestros. Solo el pago completo activa la cobertura.
            </Text>
          </Card>

          <Button
            title="ENVIAR ABONO  ✓"
            onPress={handleSubmit}
            loading={loading}
            size="lg"
            style={{ marginTop: spacing.xl }}
          />
        </ScrollView>
      </SafeAreaView>

  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: spacing.lg, paddingBottom: 40 },
  folioLabel: { ...typography.captionBold, color: colors.gray500, marginBottom: spacing.md },
  sectionTitle: {
    ...typography.captionBold,
    color: colors.gray500,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: spacing.sm,
  },
  row: { ...typography.body, color: colors.gray700, marginBottom: 2 },
  bold: { fontWeight: '700', color: colors.gray900 },
  maxHint: { ...typography.caption, color: colors.gray400, marginTop: -spacing.sm, marginBottom: spacing.lg },
  fieldLabel: {
    ...typography.captionBold,
    color: colors.gray700,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: spacing.sm,
  },
  methodRow: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginBottom: spacing.xl },
  methodChip: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    backgroundColor: colors.gray100,
  },
  methodChipActive: { backgroundColor: colors.primary },
  methodText: { ...typography.captionBold, color: colors.gray600 },
  methodTextActive: { color: colors.white },
  photoBtn: {
    backgroundColor: colors.gray100,
    borderRadius: radius.md,
    padding: spacing.xl,
    alignItems: 'center',
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: colors.gray300,
  },
  photoBtnText: { ...typography.bodyBold, color: colors.primary },
});
