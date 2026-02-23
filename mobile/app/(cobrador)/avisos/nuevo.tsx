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
import { formatMoney, formatDateFull } from '@/utils/format';

const MOCK = {
  folio: '18405',
  client: 'María López',
  cobrador: 'Edgar Ramírez',
  payment_number: 3,
  amount: '1200.00',
  status: 'Pendiente',
};

const REASONS = [
  'Cliente no estaba',
  'No tenía efectivo',
  'Pagará después',
  'Otro (especificar)',
];

export default function AvisoVisitaScreen() {
  const { folio } = useLocalSearchParams<{ folio: string }>();
  const router = useRouter();
  const [selectedReason, setSelectedReason] = useState<number | null>(0);
  const [otherText, setOtherText] = useState('');

  const now = new Date();
  const dateStr = formatDateFull(now.toISOString());
  const timeStr = now.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: true });

  const handleSubmit = () => {
    if (selectedReason === null) return Alert.alert('Error', 'Selecciona qué ocurrió');
    Alert.alert('✅ Aviso registrado', 'El aviso de visita fue guardado exitosamente.', [
      { text: 'OK', onPress: () => router.back() },
    ]);
  };

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={{ width: 40 }}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.headerTitle}>Aviso de Visita</Text>
          <Text style={styles.headerSub}>F: {MOCK.folio} · {MOCK.client}</Text>
        </View>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scroll}>
        {/* Detalles de la visita card */}
        <View style={styles.detailCard}>
          <View style={styles.detailHeader}>
            <Text style={styles.detailTitle}>DETALLES DE LA VISITA</Text>
            <View style={styles.statusBadge}>
              <Text style={styles.statusText}>{MOCK.status}</Text>
            </View>
          </View>

          {/* Grid 2x2 */}
          <View style={styles.gridRow}>
            <View style={styles.gridCol}>
              <Text style={styles.gridLabel}>Cliente</Text>
              <Text style={styles.gridValue}>{MOCK.client}</Text>
            </View>
            <View style={styles.gridCol}>
              <Text style={styles.gridLabel}>Folio</Text>
              <Text style={styles.gridValue}>{MOCK.folio}</Text>
            </View>
          </View>

          <View style={styles.gridDivider} />

          <View style={styles.gridRow}>
            <View style={styles.gridCol}>
              <Text style={styles.gridLabel}>Pago Esperado</Text>
              <Text style={styles.gridValue}>#{MOCK.payment_number} | {formatMoney(MOCK.amount)}</Text>
            </View>
            <View style={styles.gridCol}>
              <Text style={styles.gridLabel}>Cobrador</Text>
              <Text style={styles.gridValue}>{MOCK.cobrador}</Text>
            </View>
          </View>

          <View style={styles.gridDivider} />

          <View>
            <Text style={styles.gridLabel}>Fecha y Hora</Text>
            <View style={{ flexDirection: 'row', alignItems: 'center', marginTop: 4 }}>
              <Text style={{ fontSize: 14, color: colors.primary, marginRight: 6 }}>🕐</Text>
              <Text style={styles.dateTimeValue}>{dateStr} {timeStr}</Text>
            </View>
          </View>
        </View>

        {/* ¿Qué ocurrió? */}
        <Text style={styles.sectionTitle}>¿Qué ocurrió?</Text>

        {REASONS.map((reason, i) => (
          <Pressable
            key={i}
            style={[styles.radioCard, selectedReason === i && styles.radioCardActive]}
            onPress={() => setSelectedReason(i)}
          >
            <View style={[styles.radioOuter, selectedReason === i && styles.radioOuterActive]}>
              {selectedReason === i && <View style={styles.radioInner} />}
            </View>
            <Text style={styles.radioText}>{reason}</Text>
          </Pressable>
        ))}

        {selectedReason === 3 && (
          <TextInput
            style={styles.otherInput}
            placeholder="Especifica el motivo..."
            placeholderTextColor="#B0B0BE"
            value={otherText}
            onChangeText={setOtherText}
            multiline
          />
        )}

        {/* Evidencia */}
        <View style={styles.evidenceHeader}>
          <Text style={styles.sectionTitle}>Evidencia</Text>
          <Text style={styles.requiredText}>Obligatorio</Text>
        </View>

        <Pressable style={styles.photoArea}>
          <View style={styles.cameraIcon}>
            <Text style={{ fontSize: 24 }}>📸</Text>
          </View>
          <Text style={styles.photoText}>Foto del aviso colocado</Text>
        </Pressable>

        {/* Imprimir BT */}
        <Pressable style={styles.printBtn}>
          <Text style={{ fontSize: 18, marginRight: 8 }}>🖨️</Text>
          <Text style={styles.printText}>Imprimir por BT</Text>
        </Pressable>

        <View style={{ height: 100 }} />
      </ScrollView>

      {/* Bottom button */}
      <View style={styles.bottomBar}>
        <Pressable style={styles.submitBtn} onPress={handleSubmit}>
          <Text style={styles.submitText}>REGISTRAR AVISO</Text>
          <Text style={{ color: colors.white, fontSize: 16, marginLeft: 8 }}>✓</Text>
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
  headerTitle: { fontSize: 18, fontWeight: '700', color: colors.white },
  headerSub: { fontSize: 14, color: 'rgba(255,255,255,0.85)', marginTop: 2 },

  scrollView: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: 16 },

  // Detail card
  detailCard: {
    backgroundColor: colors.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    padding: 20,
    marginBottom: 24,
  },
  detailHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  detailTitle: { fontSize: 12, fontWeight: '700', color: '#333', letterSpacing: 1 },
  statusBadge: {
    backgroundColor: '#FFF3CD',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: { fontSize: 12, fontWeight: '600', color: '#856404' },

  gridRow: { flexDirection: 'row', marginBottom: 4 },
  gridCol: { flex: 1 },
  gridLabel: { fontSize: 12, color: '#999' },
  gridValue: { fontSize: 16, fontWeight: '700', color: '#1A1A1A', marginTop: 4 },
  gridDivider: { height: 1, backgroundColor: '#EEE', marginVertical: 16 },

  dateTimeValue: { fontSize: 14, fontWeight: '600', color: colors.primary },

  // Qué ocurrió
  sectionTitle: { fontSize: 20, fontWeight: '700', color: '#1A1A1A', marginBottom: 16 },

  radioCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: '#E8E8E8',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  radioCardActive: { borderColor: colors.primary },
  radioOuter: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#CCC',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  radioOuterActive: { borderColor: colors.primary },
  radioInner: { width: 12, height: 12, borderRadius: 6, backgroundColor: colors.primary },
  radioText: { fontSize: 15, color: '#333' },

  otherInput: {
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: '#E8E8E8',
    borderRadius: 12,
    padding: 16,
    fontSize: 15,
    color: '#1A1A1A',
    minHeight: 80,
    textAlignVertical: 'top',
    marginBottom: 12,
  },

  // Evidencia
  evidenceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 16,
  },
  requiredText: { fontSize: 13, fontWeight: '600', color: '#E53935' },

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
  cameraIcon: {
    width: 48,
    height: 48,
    borderRadius: 10,
    backgroundColor: 'rgba(74,58,232,0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  photoText: { fontSize: 14, color: colors.primary, fontWeight: '500' },

  printBtn: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderWidth: 2,
    borderColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 14,
  },
  printText: { fontSize: 16, fontWeight: '700', color: colors.primary },

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
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 4,
  },
  submitText: { fontSize: 16, fontWeight: '700', color: colors.white, letterSpacing: 1 },
});
