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
import { useRouter } from 'expo-router';
import { Card, Button, Input, SectionHeader } from '@/components/ui';
import { colors, spacing, radius } from '@/theme';
import { formatMoney } from '@/utils/format';

const MOCK_COLLECTORS = [
  {
    id: 1, name: 'Edgar Ramírez',
    items: [
      { folio: '18405', amount: '1200.00' },
      { folio: '18502', amount: '850.00' },
      { folio: '18310', amount: '1200.00' },
    ],
    expectedTotal: '3250.00',
  },
];

export default function ConfirmarEfectivo() {
  const router = useRouter();
  const [collector] = useState(MOCK_COLLECTORS[0]);
  const [receivedAmount, setReceivedAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ expected: string; received: string; diff: number } | null>(null);

  const receivedNum = parseFloat(receivedAmount) || 0;
  const expectedNum = parseFloat(collector.expectedTotal);
  const liveDiff = receivedAmount ? receivedNum - expectedNum : null;

  const handleConfirm = () => {
    if (!receivedAmount) {
      Alert.alert('Requerido', 'Ingresa el monto físico recibido');
      return;
    }
    setLoading(true);
    setTimeout(() => {
      setResult({ expected: collector.expectedTotal, received: receivedAmount, diff: receivedNum - expectedNum });
      setLoading(false);
    }, 500);
  };

  // ── Pantalla de resultado ──
  if (result) {
    const hasDebt = result.diff < 0;
    return (
      <SafeAreaView edges={['top']} style={styles.screen}>
        <View style={styles.header}>
          <Pressable onPress={() => { setResult(null); router.back(); }}>
            <Text style={styles.backArrow}>←</Text>
          </Pressable>
          <Text style={styles.headerTitle}>Efectivo Confirmado</Text>
          <View style={{ width: 22 }} />
        </View>
        <ScrollView contentContainerStyle={[styles.scroll, { alignItems: 'center', paddingTop: 40 }]}>
          <Text style={{ fontSize: 56, marginBottom: 16 }}>✅</Text>
          <Text style={styles.resultTitle}>Efectivo confirmado</Text>
          <Text style={styles.resultName}>{collector.name}</Text>

          <Text style={styles.resultRow}>{formatMoney(result.received)} recibidos</Text>
          <Text style={styles.resultRow}>{formatMoney(result.expected)} esperados</Text>

          {hasDebt && (
            <Card style={styles.debtCard}>
              <Text style={styles.debtTitle}>Deuda registrada:</Text>
              <Text style={styles.debtAmount}>{formatMoney(Math.abs(result.diff).toFixed(2))} · {collector.name}</Text>
              <Text style={styles.debtNote}>(se descuenta de sus comisiones)</Text>
              <View style={styles.debtDivider} />
              <Text style={styles.debtNote}>
                El pago del CLIENTE se aplica por {formatMoney(result.expected)} (monto completo)
              </Text>
            </Card>
          )}

          {/* Botón imprimir (de V2) */}
          <Pressable style={styles.printBtn}>
            <Text style={styles.printIcon}>🖨️</Text>
            <Text style={styles.printText}>Imprimir recibo de confirmación</Text>
          </Pressable>

          <Button
            title="Listo"
            onPress={() => { setResult(null); router.back(); }}
            size="lg"
            style={{ width: '100%', marginTop: 24 }}
          />
        </ScrollView>
      </SafeAreaView>
    );
  }

  // ── Pantalla principal ──
  return (
    <SafeAreaView edges={['top']} style={styles.screen}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()}>
          <Text style={styles.backArrow}>←</Text>
        </Pressable>
        <Text style={styles.headerTitle}>Confirmar Efectivo</Text>
        <View style={{ width: 22 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scroll}>
        {/* Cobrador seleccionado */}
        <Text style={styles.fieldLabel}>COBRADOR SELECCIONADO</Text>
        <Card>
          <View style={styles.collectorRow}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>ER</Text>
            </View>
            <View>
              <Text style={styles.collectorName}>{collector.name}</Text>
              <Text style={styles.collectorSub}>ID: COB-{collector.id} · Ruta Centro</Text>
            </View>
          </View>
        </Card>

        {/* Desglose */}
        <Text style={styles.fieldLabel}>DESGLOSE DE FOLIOS</Text>
        <Card>
          {collector.items.map((item, i) => (
            <View key={item.folio}>
              {i > 0 && <View style={styles.itemDivider} />}
              <View style={styles.itemRow}>
                <View>
                  <Text style={styles.itemFolioLabel}>Folio</Text>
                  <Text style={styles.itemFolio}>F:{item.folio}</Text>
                </View>
                <Text style={styles.itemAmount}>{formatMoney(item.amount)}</Text>
              </View>
            </View>
          ))}
          <View style={styles.totalDivider} />
          <View style={styles.itemRow}>
            <Text style={styles.totalLabel}>Total esperado:</Text>
            <Text style={styles.totalAmount}>{formatMoney(collector.expectedTotal)}</Text>
          </View>
        </Card>

        {/* Monto recibido */}
        <Input
          label="MONTO RECIBIDO EN FÍSICO"
          prefix="$"
          placeholder="0.00"
          value={receivedAmount}
          onChangeText={setReceivedAmount}
          keyboardType="decimal-pad"
        />

        {/* Desglose en vivo (V2 — diferencia visible) */}
        {liveDiff !== null && (
          <Card style={{ backgroundColor: liveDiff < 0 ? '#FFF0F0' : colors.successBg }}>
            <View style={styles.breakdownRow}>
              <Text style={styles.breakdownLabel}>Esperado</Text>
              <Text style={styles.breakdownValue}>{formatMoney(collector.expectedTotal)}</Text>
            </View>
            <View style={styles.breakdownRow}>
              <Text style={styles.breakdownLabel}>Recibido</Text>
              <Text style={styles.breakdownValue}>{formatMoney(receivedAmount)}</Text>
            </View>
            <View style={[styles.breakdownRow, { marginTop: 8, paddingTop: 8, borderTopWidth: 1, borderTopColor: liveDiff < 0 ? '#FEE2E2' : '#BBF7D0' }]}>
              <Text style={[styles.breakdownLabel, { fontWeight: '700' }]}>DIFERENCIA</Text>
              <Text style={[styles.breakdownDiff, { color: liveDiff < 0 ? colors.error : colors.success }]}>
                {liveDiff >= 0 ? '+' : ''}{formatMoney(liveDiff.toFixed(2))}
              </Text>
            </View>
            {liveDiff < 0 && (
              <View style={styles.debtWarning}>
                <Text style={styles.debtWarningText}>⚠️ DEUDA DEL COBRADOR</Text>
              </View>
            )}
          </Card>
        )}

        <Button
          title="CONFIRMAR RECEPCIÓN  ✓"
          onPress={handleConfirm}
          loading={loading}
          size="lg"
          style={{ marginTop: 20 }}
        />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 20, paddingVertical: 14, backgroundColor: colors.primary,
  },
  backArrow: { fontSize: 22, color: colors.white },
  headerTitle: { fontSize: 18, fontWeight: '700', color: colors.white },
  scroll: { padding: 20, paddingBottom: 100 },
  fieldLabel: { fontSize: 12, fontWeight: '700', color: '#6B7280', letterSpacing: 1, marginBottom: 8, marginTop: 16 },

  // Collector
  collectorRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  avatar: { width: 48, height: 48, borderRadius: 24, backgroundColor: colors.primaryBg, justifyContent: 'center', alignItems: 'center' },
  avatarText: { fontSize: 16, fontWeight: '700', color: colors.primary },
  collectorName: { fontSize: 16, fontWeight: '700', color: colors.textDark },
  collectorSub: { fontSize: 13, color: colors.textLight, marginTop: 2 },

  // Items
  itemRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 8 },
  itemDivider: { height: 1, backgroundColor: colors.divider },
  itemFolioLabel: { fontSize: 11, color: colors.textLight },
  itemFolio: { fontSize: 15, fontWeight: '600', color: colors.textDark },
  itemAmount: { fontSize: 16, fontWeight: '700', color: colors.textDark },
  totalDivider: { height: 2, backgroundColor: colors.textDark, marginVertical: 8 },
  totalLabel: { fontSize: 15, fontWeight: '700', color: colors.textDark },
  totalAmount: { fontSize: 20, fontWeight: '800', color: colors.success },

  // Breakdown (V2)
  breakdownRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
  breakdownLabel: { fontSize: 14, color: '#6B7280' },
  breakdownValue: { fontSize: 14, fontWeight: '600', color: colors.textDark },
  breakdownDiff: { fontSize: 20, fontWeight: '800' },
  debtWarning: {
    marginTop: 12, backgroundColor: colors.error, borderRadius: 8,
    paddingVertical: 10, paddingHorizontal: 16, alignItems: 'center',
  },
  debtWarningText: { fontSize: 13, fontWeight: '700', color: colors.white, letterSpacing: 0.5 },

  // Result screen
  resultTitle: { fontSize: 24, fontWeight: '700', color: colors.textDark, marginBottom: 4 },
  resultName: { fontSize: 18, fontWeight: '500', color: '#6B7280', marginBottom: 24 },
  resultRow: { fontSize: 16, color: '#6B7280', marginBottom: 4 },
  debtCard: { backgroundColor: '#FFF0F0', marginTop: 24, width: '100%' },
  debtTitle: { fontSize: 16, fontWeight: '700', color: colors.error },
  debtAmount: { fontSize: 20, fontWeight: '800', color: colors.error, marginTop: 4 },
  debtNote: { fontSize: 13, color: '#6B7280', marginTop: 4 },
  debtDivider: { height: 1, backgroundColor: '#FEE2E2', marginVertical: 12 },
  printBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    marginTop: 24, padding: 16, borderRadius: 12,
    backgroundColor: colors.white, borderWidth: 1, borderColor: colors.border, width: '100%',
  },
  printIcon: { fontSize: 20 },
  printText: { fontSize: 15, fontWeight: '600', color: colors.primary },
});
