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
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
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

export default function NuevoCobro() {
  const { folio } = useLocalSearchParams<{ folio: string }>();
  const router = useRouter();

  const expectedAmount = '1200.00'; // TODO: viene del folio detail

  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState<PaymentMethod | null>(null);
  const [receiptNumber, setReceiptNumber] = useState('');
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const amountDiffers = amount && amount !== expectedAmount;

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permisos', 'Se necesita acceso a la cámara');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      quality: 0.7,
      allowsEditing: false,
    });
    if (!result.canceled && result.assets[0]) {
      setPhotoUri(result.assets[0].uri);
    }
  };

  const handleSubmit = async () => {
    if (!amount || !method || !receiptNumber) {
      Alert.alert('Campos requeridos', 'Completa monto, método de pago y número de recibo');
      return;
    }

    setLoading(true);
    try {
      // Obtener GPS
      const { status } = await Location.requestForegroundPermissionsAsync();
      let lat = 0, lng = 0;
      if (status === 'granted') {
        const loc = await Location.getCurrentPositionAsync({});
        lat = loc.coords.latitude;
        lng = loc.coords.longitude;
      }

      // TODO: upload photo + createProposal
      // const photoUrl = photoUri ? await uploadPhoto(photoUri) : undefined;
      // await createProposal({ folio, payment_number, amount, method, receipt_number: receiptNumber, receipt_photo_url: photoUrl, lat, lng, is_partial: false });

      Alert.alert(
        '✅ Propuesta enviada',
        `F: ${folio} · ${formatMoney(amount)} · ${method}\n\nRecibirás una notificación cuando sea aprobada.`,
        [
          { text: 'Ver mis propuestas', onPress: () => router.push('/(cobrador)/propuestas') },
          { text: 'Siguiente folio →', onPress: () => router.back() },
        ]
      );
    } catch (err: any) {
      Alert.alert('Error', err.message || 'No se pudo enviar la propuesta');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Stack.Screen options={{ title: 'Registrar Cobro', headerBackTitle: 'Atrás' }} />
      <SafeAreaView edges={[]} style={styles.container}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text style={styles.folioLabel}>F: {folio}</Text>

          {/* Monto esperado */}
          <Card>
            <Text style={styles.sectionTitle}>DETALLE DEL COBRO</Text>
            <Text style={styles.detail}>Monto esperado:</Text>
            <Text style={styles.expectedAmount}>{formatMoney(expectedAmount)}</Text>
          </Card>

          {/* Monto cobrado */}
          <Input
            label="MONTO COBRADO *"
            placeholder="0.00"
            value={amount}
            onChangeText={setAmount}
            keyboardType="decimal-pad"
          />
          {amountDiffers && (
            <Text style={styles.amountWarning}>
              ⚠️ Monto ingresado difiere del monto de la póliza
            </Text>
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

          {/* Número de recibo */}
          <Input
            label="NÚMERO DE RECIBO *"
            placeholder="Recibo #"
            value={receiptNumber}
            onChangeText={setReceiptNumber}
          />

          {/* Foto del recibo */}
          <Text style={styles.fieldLabel}>FOTO DEL RECIBO/BAUCHER</Text>
          <Pressable style={styles.photoBtn} onPress={takePhoto}>
            <Text style={styles.photoBtnText}>
              {photoUri ? '✓ Foto adjunta — Tomar otra' : '📷 Tomar foto'}
            </Text>
            <Text style={styles.photoSub}>(opcional pero recomendado)</Text>
          </Pressable>

          {/* GPS */}
          <View style={styles.gpsRow}>
            <Text style={styles.gpsText}>📍 GPS: se capturará al enviar</Text>
          </View>

          {/* Enviar */}
          <Button
            title="ENVIAR PROPUESTA  ✓"
            onPress={handleSubmit}
            loading={loading}
            size="lg"
            style={{ marginTop: spacing.xl }}
          />
          <Text style={styles.disclaimer}>
            ℹ️ Quedará pendiente de autorización de gerencia
          </Text>
        </ScrollView>
      </SafeAreaView>
    </>
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
  detail: { ...typography.body, color: colors.gray600 },
  expectedAmount: { ...typography.money, color: colors.gray900, marginTop: spacing.xs },

  amountWarning: { ...typography.caption, color: colors.warning, marginTop: -spacing.sm, marginBottom: spacing.md },

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
    marginBottom: spacing.xl,
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: colors.gray300,
  },
  photoBtnText: { ...typography.bodyBold, color: colors.primary },
  photoSub: { ...typography.caption, color: colors.gray400, marginTop: 4 },

  gpsRow: {
    backgroundColor: colors.successLight,
    padding: spacing.md,
    borderRadius: radius.md,
  },
  gpsText: { ...typography.caption, color: colors.success },

  disclaimer: { ...typography.caption, color: colors.gray400, textAlign: 'center', marginTop: spacing.md },
});
