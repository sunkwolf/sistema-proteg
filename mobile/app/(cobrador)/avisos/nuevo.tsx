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
import { Card, Button } from '@/components/ui';
import { colors, spacing, typography, radius } from '@/theme';
import { VisitReason } from '@/types';

const REASONS: { key: VisitReason; label: string }[] = [
  { key: 'no_estaba', label: 'Cliente no estaba' },
  { key: 'sin_efectivo', label: 'No tenía efectivo' },
  { key: 'pagara_despues', label: 'Pagará después' },
  { key: 'otro', label: 'Otro (especificar)' },
];

export default function AvisoVisita() {
  const { folio } = useLocalSearchParams<{ folio: string }>();
  const router = useRouter();

  const [reason, setReason] = useState<VisitReason | null>(null);
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permisos', 'Se necesita acceso a la cámara para la evidencia');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({ quality: 0.7 });
    if (!result.canceled && result.assets[0]) {
      setPhotoUri(result.assets[0].uri);
    }
  };

  const handleSubmit = async () => {
    if (!reason) {
      Alert.alert('Requerido', 'Selecciona qué ocurrió');
      return;
    }
    if (!photoUri) {
      Alert.alert('Foto obligatoria', 'Toma una foto del aviso colocado en la puerta o entregado');
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

      // TODO: upload photo + createVisitNotice

      Alert.alert('✅ Aviso registrado', `F: ${folio} — Aviso guardado con éxito`, [
        { text: 'OK', onPress: () => router.back() },
      ]);
    } catch (err: any) {
      Alert.alert('Error', err.message || 'No se pudo registrar el aviso');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Stack.Screen options={{ title: 'Aviso de Visita', headerBackTitle: 'Atrás' }} />
      <SafeAreaView edges={[]} style={styles.container}>
        <ScrollView contentContainerStyle={styles.scroll}>
          {/* Datos pre-llenados */}
          <Card>
            <Text style={styles.sectionTitle}>DATOS DEL AVISO</Text>
            <Text style={styles.detail}>Folio: {folio}</Text>
            <Text style={styles.detail}>
              Fecha: {new Date().toLocaleDateString('es-MX', {
                weekday: 'long', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
              })}
            </Text>
          </Card>

          {/* ¿Qué ocurrió? */}
          <Text style={styles.fieldLabel}>¿QUÉ OCURRIÓ? *</Text>
          {REASONS.map((r) => (
            <Pressable
              key={r.key}
              onPress={() => setReason(r.key)}
              style={[styles.reasonOption, reason === r.key && styles.reasonActive]}
            >
              <Text style={[styles.radioCircle, reason === r.key && styles.radioFilled]}>
                {reason === r.key ? '●' : '○'}
              </Text>
              <Text style={[styles.reasonText, reason === r.key && styles.reasonTextActive]}>
                {r.label}
              </Text>
            </Pressable>
          ))}

          {/* Foto de evidencia */}
          <Text style={[styles.fieldLabel, { marginTop: spacing.xl }]}>
            FOTO DE EVIDENCIA *
          </Text>
          <Text style={styles.photoHint}>
            (Aviso colocado en puerta o entregado a alguien)
          </Text>
          <Pressable style={styles.photoBtn} onPress={takePhoto}>
            <Text style={styles.photoBtnText}>
              {photoUri ? '✓ Foto tomada — Tomar otra' : '📷 TOMAR FOTO'}
            </Text>
            <Text style={styles.photoSub}>(Obligatoria)</Text>
          </Pressable>

          {/* TODO: botón imprimir por BT */}
          <Pressable style={styles.printBtn}>
            <Text style={styles.printText}>🖨️ Imprimir por BT (opcional)</Text>
          </Pressable>

          <Button
            title="REGISTRAR AVISO  ✓"
            onPress={handleSubmit}
            loading={loading}
            size="lg"
            style={{ marginTop: spacing.xl }}
          />
        </ScrollView>
      </SafeAreaView>
    </>
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
  detail: { ...typography.body, color: colors.gray700, marginBottom: 2 },
  fieldLabel: {
    ...typography.captionBold,
    color: colors.gray700,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: spacing.sm,
    marginTop: spacing.lg,
  },
  reasonOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    marginBottom: spacing.xs,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.gray200,
  },
  reasonActive: {
    borderColor: colors.primary,
    backgroundColor: '#EEF2FF',
  },
  radioCircle: { fontSize: 18, color: colors.gray400, marginRight: spacing.md },
  radioFilled: { color: colors.primary },
  reasonText: { ...typography.body, color: colors.gray700 },
  reasonTextActive: { color: colors.primary, fontWeight: '600' },
  photoHint: { ...typography.caption, color: colors.gray400, marginBottom: spacing.sm },
  photoBtn: {
    backgroundColor: colors.gray100,
    borderRadius: radius.md,
    padding: spacing['2xl'],
    alignItems: 'center',
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: colors.gray300,
  },
  photoBtnText: { ...typography.bodyBold, color: colors.primary },
  photoSub: { ...typography.small, color: colors.gray400, marginTop: 4 },
  printBtn: {
    alignItems: 'center',
    padding: spacing.lg,
    marginTop: spacing.md,
  },
  printText: { ...typography.body, color: colors.gray500 },
});
