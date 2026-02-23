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
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { ScreenHeader } from '@/components/ui';
import { colors } from '@/theme';
import { formatMoney } from '@/utils/format';

interface FolioEntry {
  folio: string;
  amount: string;
}

const MOCK = {
  cobrador: { name: 'Edgar Ramírez', id: 'COB-1', zone: 'Ruta Norte', initials: 'ER' },
  folios: [
    { folio: '18405', amount: '1200.00' },
    { folio: '18502', amount: '850.00' },
    { folio: '18310', amount: '1200.00' },
  ] as FolioEntry[],
};

export default function ConfirmarEfectivoScreen() {
  const router = useRouter();
  const [receivedAmount, setReceivedAmount] = useState('3050.00');
  const [confirmed, setConfirmed] = useState(false);

  const expectedTotal = MOCK.folios.reduce((s, f) => s + parseFloat(f.amount), 0);
  const received = parseFloat(receivedAmount) || 0;
  const diff = received - expectedTotal;
  const hasDebt = diff < 0;

  const handleConfirm = () => {
    if (hasDebt) {
      Alert.alert(
        'Deuda detectada',
        `Hay una diferencia de ${formatMoney(String(Math.abs(diff)))}. Se registrará como deuda del cobrador.`,
        [
          { text: 'Cancelar', style: 'cancel' },
          { text: 'Confirmar', onPress: () => setConfirmed(true) },
        ]
      );
    } else {
      setConfirmed(true);
    }
  };

  if (confirmed) {
    return (
      <SafeAreaView edges={['top']} style={styles.safe}>
        <ScreenHeader title="Efectivo Confirmado" />
        <ScrollView style={styles.scrollView} contentContainerStyle={[styles.scroll, { alignItems: 'center', paddingTop: 60 }]}>
          <View style={styles.successIcon}>
            <Text style={{ fontSize: 40 }}>✅</Text>
          </View>
          <Text style={styles.successTitle}>Efectivo confirmado</Text>
          <Text style={styles.successSub}>{MOCK.cobrador.name}</Text>

          <Text style={styles.successDetail}>{formatMoney(receivedAmount)} recibidos</Text>
          <Text style={styles.successDetail}>{formatMoney(String(expectedTotal))} esperados</Text>

          {hasDebt && (
            <>
              <Text style={styles.debtLabel}>Deuda registrada:</Text>
              <Text style={styles.debtAmount}>{formatMoney(String(Math.abs(diff)))} · {MOCK.cobrador.name}</Text>
              <Text style={styles.debtNote}>(se descuenta de sus comisiones)</Text>
            </>
          )}

          <View style={styles.successDivider} />
          <Text style={styles.clientNote}>
            El pago del CLIENTE se aplica por {formatMoney(String(expectedTotal))} (monto completo)
          </Text>

          <Pressable style={styles.printRow}>
            <Text style={{ fontSize: 18, marginRight: 10 }}>🖨️</Text>
            <Text style={styles.printText}>Imprimir recibo de confirmación</Text>
          </Pressable>

          <Pressable style={styles.btnDone} onPress={() => router.back()}>
            <Text style={styles.btnDoneText}>Listo</Text>
          </Pressable>
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      <ScreenHeader title="Confirmar Efectivo" rightIcon="help" />

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scroll}>
        {/* Cobrador card */}
        <View style={styles.card}>
          <Text style={styles.sectionLabel}>COBRADOR SELECCIONADO</Text>
          <View style={styles.cobradorRow}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>{MOCK.cobrador.initials}</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.cobradorName}>{MOCK.cobrador.name}</Text>
              <Text style={styles.cobradorMeta}>ID: {MOCK.cobrador.id} · {MOCK.cobrador.zone}</Text>
            </View>
            <Text style={{ fontSize: 18, color: '#CCC' }}>✓</Text>
          </View>
        </View>

        {/* Desglose de folios */}
        <View style={styles.card}>
          <View style={styles.rowBetween}>
            <Text style={styles.sectionLabel}>DESGLOSE DE FOLIOS</Text>
            <View style={styles.countBadge}>
              <Text style={styles.countBadgeText}>{MOCK.folios.length} folios</Text>
            </View>
          </View>

          {MOCK.folios.map((f, i) => (
            <View key={i} style={[styles.folioRow, i > 0 && styles.folioBorder]}>
              <View style={styles.folioLeft}>
                <Text style={{ fontSize: 14, marginRight: 8 }}>📋</Text>
                <View>
                  <Text style={styles.folioLabel}>Folio</Text>
                  <Text style={styles.folioNum}>F:{f.folio}</Text>
                </View>
              </View>
              <Text style={styles.folioAmount}>{formatMoney(f.amount)}</Text>
            </View>
          ))}

          <View style={styles.totalDivider} />
          <View style={styles.rowBetween}>
            <Text style={styles.totalLabel}>Total esperado:</Text>
            <Text style={styles.totalAmount}>{formatMoney(String(expectedTotal))}</Text>
          </View>
        </View>

        {/* Monto físico recibido */}
        <Text style={styles.fieldLabel}>MONTO FÍSICO RECIBIDO</Text>
        <View style={styles.amountInput}>
          <Text style={styles.currencyPrefix}>$</Text>
          <TextInput
            style={styles.amountField}
            value={receivedAmount}
            onChangeText={setReceivedAmount}
            keyboardType="decimal-pad"
          />
          <Text style={{ fontSize: 16, color: '#CCC' }}>✏️</Text>
        </View>

        {/* Breakdown */}
        {receivedAmount && (
          <View style={[styles.card, hasDebt && { borderWidth: 1, borderColor: '#FF3B30' }]}>
            <View style={styles.breakdownRow}>
              <Text style={styles.breakdownLabel}>Esperado</Text>
              <Text style={styles.breakdownValue}>{formatMoney(String(expectedTotal))}</Text>
            </View>
            <View style={styles.breakdownRow}>
              <Text style={styles.breakdownLabel}>Recibido</Text>
              <Text style={styles.breakdownValue}>{formatMoney(receivedAmount)}</Text>
            </View>
            <View style={[styles.breakdownRow, styles.diffRow]}>
              <Text style={[styles.breakdownLabel, { fontWeight: '700' }]}>DIFERENCIA</Text>
              <Text style={[styles.breakdownValue, { color: hasDebt ? '#FF3B30' : '#22C55E', fontWeight: '800' }]}>
                {formatMoney(String(diff))}
              </Text>
            </View>

            {hasDebt && (
              <View style={styles.warningBanner}>
                <Text style={{ fontSize: 14, marginRight: 8 }}>⚠️</Text>
                <Text style={styles.warningText}>Hay una diferencia</Text>
                <View style={styles.debtBadge}>
                  <Text style={styles.debtBadgeText}>DEUDA DETECTADA</Text>
                </View>
              </View>
            )}
          </View>
        )}

        <View style={{ height: 100 }} />
      </ScrollView>

      <View style={styles.bottomBar}>
        <Pressable style={styles.btnConfirm} onPress={handleConfirm}>
          <Text style={styles.btnConfirmText}>CONFIRMAR RECEPCIÓN</Text>
          <Text style={{ color: colors.white, fontSize: 16, marginLeft: 8 }}>✓</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.primary },
  scrollView: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: 16 },

  card: {
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 1,
  },

  sectionLabel: { fontSize: 11, fontWeight: '700', color: '#8E8E93', letterSpacing: 1, marginBottom: 12 },

  // Cobrador
  cobradorRow: { flexDirection: 'row', alignItems: 'center' },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  avatarText: { fontSize: 16, fontWeight: '700', color: colors.white },
  cobradorName: { fontSize: 16, fontWeight: '700', color: '#1A1A1A' },
  cobradorMeta: { fontSize: 13, color: '#8E8E93', marginTop: 2 },

  // Folios
  rowBetween: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  countBadge: {
    backgroundColor: '#E8E7FB',
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 10,
  },
  countBadgeText: { fontSize: 12, fontWeight: '600', color: colors.primary },

  folioRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
  },
  folioBorder: { borderTopWidth: 1, borderTopColor: '#F0F0F5' },
  folioLeft: { flexDirection: 'row', alignItems: 'center' },
  folioLabel: { fontSize: 11, color: '#8E8E93' },
  folioNum: { fontSize: 15, fontWeight: '700', color: '#1A1A1A' },
  folioAmount: { fontSize: 16, fontWeight: '700', color: '#1A1A1A' },

  totalDivider: { height: 2, backgroundColor: '#E5E5EA', marginVertical: 12 },
  totalLabel: { fontSize: 14, fontWeight: '600', color: '#555' },
  totalAmount: { fontSize: 20, fontWeight: '800', color: '#22C55E' },

  // Amount input
  fieldLabel: { fontSize: 11, fontWeight: '700', color: '#8E8E93', letterSpacing: 1, marginBottom: 8, marginTop: 4 },
  amountInput: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    paddingHorizontal: 16,
    height: 56,
    marginBottom: 16,
  },
  currencyPrefix: { fontSize: 18, fontWeight: '600', color: '#1A1A1A', marginRight: 4 },
  amountField: { flex: 1, fontSize: 18, color: '#1A1A1A' },

  // Breakdown
  breakdownRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  breakdownLabel: { fontSize: 14, color: '#666' },
  breakdownValue: { fontSize: 14, fontWeight: '600', color: '#1A1A1A' },
  diffRow: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#F0F0F5',
    marginBottom: 0,
  },
  warningBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF3C7',
    borderRadius: 8,
    padding: 12,
    marginTop: 12,
  },
  warningText: { fontSize: 14, fontWeight: '600', color: '#92600A', flex: 1 },
  debtBadge: {
    backgroundColor: '#FEE2E0',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  debtBadgeText: { fontSize: 10, fontWeight: '700', color: '#FF3B30', letterSpacing: 0.5 },

  // Bottom
  bottomBar: {
    backgroundColor: colors.background,
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 24,
  },
  btnConfirm: {
    flexDirection: 'row',
    backgroundColor: colors.primary,
    borderRadius: 14,
    paddingVertical: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  btnConfirmText: { fontSize: 16, fontWeight: '700', color: colors.white, letterSpacing: 0.5 },

  // Success screen
  successIcon: {
    width: 80,
    height: 80,
    borderRadius: 16,
    backgroundColor: '#E8F5E9',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  successTitle: { fontSize: 24, fontWeight: '800', color: '#1A1A1A', marginBottom: 4 },
  successSub: { fontSize: 16, color: '#8E8E93', marginBottom: 24 },
  successDetail: { fontSize: 15, color: '#666', marginBottom: 4 },
  debtLabel: { fontSize: 14, color: '#FF3B30', fontWeight: '600', marginTop: 16, marginBottom: 4 },
  debtAmount: { fontSize: 20, fontWeight: '700', color: '#FF3B30' },
  debtNote: { fontSize: 13, color: '#8E8E93', marginTop: 4 },
  successDivider: { height: 1, backgroundColor: '#E5E5EA', width: '100%', marginVertical: 20 },
  clientNote: { fontSize: 14, color: '#555', textAlign: 'center', marginBottom: 24 },
  printRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.white,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 12,
    paddingVertical: 14,
    width: '100%',
    marginBottom: 16,
  },
  printText: { fontSize: 15, fontWeight: '600', color: colors.primary },
  btnDone: {
    backgroundColor: colors.primary,
    borderRadius: 14,
    paddingVertical: 16,
    width: '100%',
    alignItems: 'center',
  },
  btnDoneText: { fontSize: 16, fontWeight: '700', color: colors.white },
});
