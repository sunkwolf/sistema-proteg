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
import { Card, Button, Input, Badge } from '@/components/ui';
import { colors, spacing, radius } from '@/theme';
import { formatMoney } from '@/utils/format';
import { ReviewDecision } from '@/types';

export default function DetalleProposalGerente() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();

  // TODO: useProposalDetail(id)
  const p = {
    folio: '18510', client: 'Roberto Sánchez', collector: 'Edgar R.',
    payment: 1, totalPayments: 7,
    amountProposed: '1401.00', amountExpected: '1401.00',
    method: 'Efectivo', receipt: 'A00147', receiptValid: true, amountsMatch: true,
    coverage: 'AMPLIA', vehicle: 'Toyota Rav4 22',
    gps: 'Tonalá, Jalisco',
  };

  const [decision, setDecision] = useState<ReviewDecision | null>(null);
  const [correctionValue, setCorrectionValue] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAction = async (d: ReviewDecision) => {
    if (d === 'rechazar' && !rejectionReason.trim()) {
      Alert.alert('Requerido', 'Indica el motivo del rechazo');
      return;
    }
    setLoading(true);
    try {
      // TODO: useReviewProposal()
      const label = d === 'aprobar' ? 'aprobada' : d === 'corregir' ? 'corregida y aprobada' : 'rechazada';
      Alert.alert('✅', `Propuesta ${label}`, [{ text: 'OK', onPress: () => router.back() }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView edges={['top']} style={styles.screen}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()}>
          <Text style={styles.backArrow}>←</Text>
        </Pressable>
        <View style={{ flex: 1, marginLeft: 12 }}>
          <Text style={styles.headerTitle}>Propuesta #{id}</Text>
          <Text style={styles.headerSub}>{p.collector} · 10:15 AM</Text>
        </View>
        <Text style={styles.menuIcon}>⋮</Text>
      </View>

      <ScrollView contentContainerStyle={styles.scroll}>
        {/* Póliza */}
        <Card>
          <Text style={styles.sectionLabel}>PÓLIZA</Text>
          <Text style={styles.clientName}>F: {p.folio} · {p.client}</Text>
          <View style={styles.vehicleRow}>
            <Text style={{ fontSize: 20, marginRight: 8 }}>🚗</Text>
            <Text style={styles.vehicleText}>{p.vehicle}</Text>
            <Badge label={p.coverage} variant="info" />
          </View>
        </Card>

        {/* Comparativa */}
        <Text style={styles.compareTitle}>Comparativa de Pago</Text>

        {/* Lo que registró */}
        <Card style={styles.compareCard}>
          <Text style={styles.sectionLabel}>LO QUE REGISTRÓ</Text>
          <Text style={styles.compareAmount}>{formatMoney(p.amountProposed)}</Text>
          <Badge label={`Pago #${p.payment} de ${p.totalPayments}`} variant="info" />
          <View style={styles.compareDetail}>
            <Text style={styles.detailRow}>💵 {p.method}</Text>
            <Text style={styles.detailRow}>🧾 Recibo: {p.receipt}</Text>
            <Pressable>
              <Text style={styles.photoLink}>🖼️ Ver foto del recibo</Text>
            </Pressable>
            <Text style={styles.detailRow}>📍 {p.gps}</Text>
          </View>
        </Card>

        {/* Lo que espera la póliza */}
        <Card style={styles.compareCard}>
          <Text style={styles.sectionLabel}>LO QUE ESPERA LA PÓLIZA</Text>
          <Text style={[styles.compareAmount, p.amountsMatch && { color: colors.success }]}>
            {formatMoney(p.amountExpected)} {p.amountsMatch ? '✅' : '⚠️'}
          </Text>
          <Text style={styles.detailRow}>Pago #{p.payment}</Text>
          <Text style={styles.detailRow}>
            Recibo {p.receipt}: {p.receiptValid ? '✅ Válido' : '❌ No encontrado'}
          </Text>
        </Card>

        {/* Botones de decisión */}
        <View style={styles.actionsBox}>
          <Button
            title="✅  APROBAR"
            variant="success"
            size="lg"
            onPress={() => handleAction('aprobar')}
            loading={loading && decision === 'aprobar'}
            style={{ marginBottom: 12 }}
          />

          <Button
            title="🔧  CORREGIR Y APROBAR"
            variant="primary"
            size="lg"
            onPress={() => setDecision(decision === 'corregir' ? null : 'corregir')}
            style={{ marginBottom: decision === 'corregir' ? 0 : 12 }}
          />
          {decision === 'corregir' && (
            <Card style={{ marginTop: 12, marginBottom: 12 }}>
              <Input label="Valor correcto" value={correctionValue} onChangeText={setCorrectionValue} prefix="$" keyboardType="decimal-pad" />
              <Button title="Confirmar corrección" onPress={() => handleAction('corregir')} loading={loading} />
            </Card>
          )}

          <Button
            title="❌  RECHAZAR"
            variant="outline"
            size="lg"
            onPress={() => setDecision(decision === 'rechazar' ? null : 'rechazar')}
            style={{ borderColor: colors.error }}
          />
          {decision === 'rechazar' && (
            <Card style={{ marginTop: 12 }}>
              <Input label="Motivo (obligatorio)" value={rejectionReason} onChangeText={setRejectionReason} multiline placeholder="Describe el motivo..." />
              <Button title="Confirmar rechazo" variant="danger" onPress={() => handleAction('rechazar')} loading={loading} />
            </Card>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  header: {
    flexDirection: 'row', alignItems: 'center', paddingHorizontal: 20, paddingVertical: 14,
    backgroundColor: colors.primary,
  },
  backArrow: { fontSize: 22, color: colors.white },
  headerTitle: { fontSize: 18, fontWeight: '700', color: colors.white },
  headerSub: { fontSize: 13, color: 'rgba(255,255,255,0.8)' },
  menuIcon: { fontSize: 22, color: colors.white },
  scroll: { padding: 20, paddingBottom: 100 },
  sectionLabel: { fontSize: 12, fontWeight: '700', color: colors.gray500, letterSpacing: 1, marginBottom: 10 },
  clientName: { fontSize: 18, fontWeight: '700', color: colors.textDark, marginBottom: 8 },
  vehicleRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  vehicleText: { fontSize: 14, color: colors.gray500, flex: 1 },
  compareTitle: { fontSize: 16, fontWeight: '700', color: colors.textDark, marginTop: 20, marginBottom: 12 },
  compareCard: { borderWidth: 1, borderColor: colors.border },
  compareAmount: { fontSize: 32, fontWeight: '700', color: colors.textDark, marginBottom: 8 },
  compareDetail: { marginTop: 12, gap: 6 },
  detailRow: { fontSize: 14, color: colors.gray500 },
  photoLink: { fontSize: 14, fontWeight: '600', color: colors.primary },
  actionsBox: { marginTop: 24 },
});
