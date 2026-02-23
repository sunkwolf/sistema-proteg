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
import { Card, Button, Input } from '@/components/ui';
import { colors, spacing, typography, radius } from '@/theme';
import { formatMoney } from '@/utils/format';
import { ReviewDecision } from '@/types';

export default function DetalleProposalGerente() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();

  // TODO: datos reales
  const proposal = {
    folio: '18510',
    client: 'Roberto Sánchez',
    collector: 'Edgar R.',
    payment: 1,
    amountProposed: '1401.00',
    amountExpected: '1401.00',
    method: 'Efectivo',
    receipt: 'A00147',
    receiptValid: true,
    amountsMatch: true,
    coverage: 'AMPLIA',
    vehicle: 'Toyota Rav4 22',
    photoUrl: null as string | null,
  };

  const [decision, setDecision] = useState<ReviewDecision | null>(null);
  const [correctionField, setCorrectionField] = useState('');
  const [correctionValue, setCorrectionValue] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!decision) return;
    if (decision === 'rechazar' && !rejectionReason.trim()) {
      Alert.alert('Requerido', 'Indica el motivo del rechazo');
      return;
    }

    setLoading(true);
    try {
      // TODO: reviewProposal(id, { decision, ... })
      const label = decision === 'aprobar' ? 'aprobada' : decision === 'corregir' ? 'corregida y aprobada' : 'rechazada';
      Alert.alert('✅ Listo', `Propuesta ${label}`, [
        { text: 'OK', onPress: () => router.back() },
      ]);
    } catch (err: any) {
      Alert.alert('Error', err.message || 'No se pudo procesar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Stack.Screen options={{ title: `Propuesta #${id}`, headerBackTitle: 'Atrás' }} />
      <SafeAreaView edges={[]} style={styles.container}>
        <ScrollView contentContainerStyle={styles.scroll}>
          {/* Póliza */}
          <Card>
            <Text style={styles.sectionTitle}>PÓLIZA</Text>
            <Text style={styles.detail}>F: {proposal.folio} · {proposal.client}</Text>
            <Text style={styles.detail}>{proposal.coverage} · {proposal.vehicle}</Text>
          </Card>

          {/* Lo que registró */}
          <Card>
            <Text style={styles.sectionTitle}>LO QUE REGISTRÓ</Text>
            <Text style={styles.detail}>Pago: #{proposal.payment}</Text>
            <Text style={styles.detail}>Monto: {formatMoney(proposal.amountProposed)}</Text>
            <Text style={styles.detail}>Método: {proposal.method}</Text>
            <Text style={styles.detail}>Recibo: {proposal.receipt}</Text>
            {proposal.photoUrl && (
              <Pressable style={styles.photoLink}>
                <Text style={styles.link}>🖼️ Ver foto recibo</Text>
              </Pressable>
            )}
            <Text style={styles.detail}>📍 Tonalá, Jal.</Text>
          </Card>

          {/* Lo que espera la póliza */}
          <Card>
            <Text style={styles.sectionTitle}>LO QUE ESPERA LA PÓLIZA</Text>
            <Text style={styles.detail}>
              Monto esperado: {formatMoney(proposal.amountExpected)}
              {proposal.amountsMatch ? ' ✅' : ' ⚠️'}
            </Text>
            <Text style={styles.detail}>
              Recibo {proposal.receipt}: {proposal.receiptValid ? 'Válido ✅' : '🔴 No encontrado'}
            </Text>
          </Card>

          {/* Decisión */}
          <Text style={styles.sectionTitle}>DECISIÓN</Text>

          <Button
            title="✅  APROBAR"
            variant="success"
            size="lg"
            onPress={() => { setDecision('aprobar'); handleSubmit(); }}
            style={{ marginBottom: spacing.md }}
          />

          <Button
            title="🔧  CORREGIR Y APROBAR"
            variant="primary"
            size="lg"
            onPress={() => setDecision('corregir')}
            style={{ marginBottom: spacing.sm }}
          />
          {decision === 'corregir' && (
            <Card style={{ marginBottom: spacing.md }}>
              <Input
                label="Campo a corregir"
                placeholder="Monto, Recibo..."
                value={correctionField}
                onChangeText={setCorrectionField}
              />
              <Input
                label="Valor correcto"
                placeholder=""
                value={correctionValue}
                onChangeText={setCorrectionValue}
              />
              <Button
                title="Confirmar corrección"
                variant="primary"
                onPress={handleSubmit}
                loading={loading}
              />
            </Card>
          )}

          <Button
            title="❌  RECHAZAR"
            variant="danger"
            size="lg"
            onPress={() => setDecision('rechazar')}
            style={{ marginBottom: spacing.sm }}
          />
          {decision === 'rechazar' && (
            <Card>
              <Input
                label="Motivo (obligatorio)"
                placeholder="Describe el motivo del rechazo..."
                value={rejectionReason}
                onChangeText={setRejectionReason}
                multiline
              />
              <Button
                title="Confirmar rechazo"
                variant="danger"
                onPress={handleSubmit}
                loading={loading}
              />
            </Card>
          )}
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
    marginTop: spacing.lg,
  },
  detail: { ...typography.body, color: colors.gray700, marginBottom: 2 },
  link: { ...typography.bodyBold, color: colors.primary },
  photoLink: { marginTop: spacing.sm },
});
