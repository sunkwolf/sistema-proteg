import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack } from 'expo-router';
import { Card, Button, Input } from '@/components/ui';
import { colors, spacing, typography, radius } from '@/theme';
import { formatMoney } from '@/utils/format';

// TODO: datos reales
const MOCK_COLLECTORS = [
  {
    id: 1,
    name: 'Edgar Ramírez',
    items: [
      { folio: '18405', amount: '1200.00' },
      { folio: '18502', amount: '850.00' },
      { folio: '18310', amount: '1200.00' },
    ],
    expectedTotal: '3250.00',
  },
];

export default function ConfirmarEfectivo() {
  const [selectedCollector, setSelectedCollector] = useState(MOCK_COLLECTORS[0]);
  const [receivedAmount, setReceivedAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    expected: string;
    received: string;
    difference: string;
    hasDebt: boolean;
  } | null>(null);

  const handleConfirm = async () => {
    if (!receivedAmount) {
      Alert.alert('Requerido', 'Ingresa el monto físico recibido');
      return;
    }

    setLoading(true);
    try {
      const expected = parseFloat(selectedCollector.expectedTotal);
      const received = parseFloat(receivedAmount);
      const diff = received - expected;

      // TODO: confirmCash API call

      setResult({
        expected: selectedCollector.expectedTotal,
        received: receivedAmount,
        difference: diff.toFixed(2),
        hasDebt: diff < 0,
      });
    } catch (err: any) {
      Alert.alert('Error', err.message || 'No se pudo confirmar');
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    const diff = parseFloat(result.difference);
    return (
      <>
        <Stack.Screen options={{ title: 'Efectivo Confirmado' }} />
        <SafeAreaView edges={[]} style={styles.container}>
          <ScrollView contentContainerStyle={[styles.scroll, { alignItems: 'center' }]}>
            <Text style={{ fontSize: 48, marginBottom: spacing.lg }}>✅</Text>
            <Text style={styles.resultTitle}>Efectivo confirmado</Text>
            <Text style={styles.resultName}>{selectedCollector.name}</Text>
            <Text style={styles.resultRow}>
              {formatMoney(result.received)} recibidos
            </Text>
            <Text style={styles.resultRow}>
              {formatMoney(result.expected)} esperados
            </Text>

            {result.hasDebt && (
              <Card style={styles.debtCard}>
                <Text style={styles.debtTitle}>Deuda registrada:</Text>
                <Text style={styles.debtAmount}>
                  {formatMoney(Math.abs(diff).toFixed(2))} · {selectedCollector.name}
                </Text>
                <Text style={styles.debtNote}>
                  (se descuenta de sus comisiones)
                </Text>
                <Text style={[styles.debtNote, { marginTop: spacing.md }]}>
                  El pago del CLIENTE se aplica por {formatMoney(result.expected)} (monto completo)
                </Text>
              </Card>
            )}

            <Button
              title="Listo"
              onPress={() => setResult(null)}
              style={{ marginTop: spacing.xl, width: '100%' }}
            />
          </ScrollView>
        </SafeAreaView>
      </>
    );
  }

  return (
    <>
      <Stack.Screen options={{ title: 'Confirmar Efectivo' }} />
      <SafeAreaView edges={[]} style={styles.container}>
        <ScrollView contentContainerStyle={styles.scroll}>
          {/* Selector cobrador */}
          <Text style={styles.fieldLabel}>COBRADOR</Text>
          <Card>
            <Text style={styles.collectorName}>{selectedCollector.name}</Text>
          </Card>

          {/* Desglose esperado */}
          <Text style={styles.sectionTitle}>EFECTIVO ESPERADO</Text>
          <Text style={styles.subLabel}>
            (según propuestas aprobadas con efectivo)
          </Text>
          <Card>
            {selectedCollector.items.map((item) => (
              <View key={item.folio} style={styles.itemRow}>
                <Text style={styles.detail}>F:{item.folio}</Text>
                <Text style={styles.detail}>{formatMoney(item.amount)}</Text>
              </View>
            ))}
            <View style={styles.divider} />
            <View style={styles.itemRow}>
              <Text style={styles.totalLabel}>Total esperado:</Text>
              <Text style={styles.totalAmount}>
                {formatMoney(selectedCollector.expectedTotal)}
              </Text>
            </View>
          </Card>

          {/* Monto recibido */}
          <Input
            label="MONTO FÍSICO RECIBIDO *"
            placeholder="0.00"
            value={receivedAmount}
            onChangeText={setReceivedAmount}
            keyboardType="decimal-pad"
          />

          {/* Preview diferencia */}
          {receivedAmount && (() => {
            const diff = parseFloat(receivedAmount) - parseFloat(selectedCollector.expectedTotal);
            return (
              <Card style={{ backgroundColor: diff < 0 ? colors.dangerLight : colors.successLight }}>
                <Text style={styles.detail}>Esperado:  {formatMoney(selectedCollector.expectedTotal)}</Text>
                <Text style={styles.detail}>Recibido:  {formatMoney(receivedAmount)}</Text>
                <Text style={[styles.totalLabel, { color: diff < 0 ? colors.danger : colors.success }]}>
                  Diferencia: {diff >= 0 ? '+' : ''}{formatMoney(diff.toFixed(2))}
                </Text>
                {diff < 0 && (
                  <Text style={{ ...typography.caption, color: colors.danger, marginTop: spacing.xs }}>
                    ⚠️ Deuda del cobrador
                  </Text>
                )}
              </Card>
            );
          })()}

          <Button
            title="CONFIRMAR RECEPCIÓN ✓"
            onPress={handleConfirm}
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
  fieldLabel: {
    ...typography.captionBold,
    color: colors.gray700,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: spacing.sm,
  },
  sectionTitle: {
    ...typography.captionBold,
    color: colors.gray500,
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginTop: spacing.lg,
    marginBottom: spacing.xs,
  },
  subLabel: { ...typography.caption, color: colors.gray400, marginBottom: spacing.md },
  collectorName: { ...typography.h3, color: colors.gray900 },
  itemRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  detail: { ...typography.body, color: colors.gray700 },
  divider: { height: 1, backgroundColor: colors.gray200, marginVertical: spacing.sm },
  totalLabel: { ...typography.bodyBold, color: colors.gray900 },
  totalAmount: { ...typography.moneySmall, color: colors.gray900 },

  // Result
  resultTitle: { ...typography.h2, color: colors.gray900, marginBottom: spacing.sm },
  resultName: { ...typography.h3, color: colors.gray700, marginBottom: spacing.lg },
  resultRow: { ...typography.body, color: colors.gray600, marginBottom: 4 },
  debtCard: { backgroundColor: colors.dangerLight, marginTop: spacing.lg, width: '100%' },
  debtTitle: { ...typography.bodyBold, color: colors.danger },
  debtAmount: { ...typography.moneySmall, color: colors.danger, marginTop: spacing.xs },
  debtNote: { ...typography.caption, color: colors.gray600, marginTop: spacing.xs },
});
