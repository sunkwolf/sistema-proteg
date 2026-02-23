import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { colors } from '@/theme';
import { formatMoney } from '@/utils/format';

export default function ExitoCobroScreen() {
  const router = useRouter();
  const { folio, amount, method, payment } = useLocalSearchParams<{
    folio: string;
    amount: string;
    method: string;
    payment: string;
  }>();

  return (
    <SafeAreaView edges={['top', 'bottom']} style={styles.safe}>
      <View style={styles.content}>
        {/* Success icon */}
        <View style={styles.successCircle}>
          <Text style={styles.checkmark}>✓</Text>
        </View>

        <Text style={styles.title}>Propuesta enviada</Text>

        {/* Reference card */}
        <View style={styles.refCard}>
          <Text style={{ fontSize: 24, marginBottom: 8 }}>📋</Text>
          <Text style={styles.refLabel}>REFERENCIA</Text>
          <View style={styles.refDivider} />
          <Text style={styles.refFolio}>F:{folio || '18405'} - Pago #{payment || '3'}</Text>
          <View style={styles.refAmountRow}>
            <Text style={styles.refAmount}>{formatMoney(amount || '1200.00')}</Text>
            <Text style={styles.refDot}>·</Text>
            <Text style={styles.refMethod}>{method || 'Efectivo'}</Text>
          </View>
        </View>

        <Text style={styles.notifText}>
          Recibirás una notificación cuando sea aprobada.
        </Text>
      </View>

      {/* Bottom buttons */}
      <View style={styles.bottomBar}>
        <Pressable style={styles.btnNext} onPress={() => router.replace('/(cobrador)/folios')}>
          <Text style={styles.btnNextText}>Siguiente folio</Text>
          <Text style={styles.btnNextArrow}>→</Text>
        </Pressable>

        <Pressable style={styles.btnProposals} onPress={() => router.replace('/(cobrador)/propuestas')}>
          <Text style={styles.btnProposalsText}>Ver mis propuestas</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.background },

  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 32,
  },

  successCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#22C55E',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  checkmark: { fontSize: 36, color: colors.white, fontWeight: '700' },

  title: { fontSize: 26, fontWeight: '800', color: '#1A1A1A', marginBottom: 32 },

  refCard: {
    backgroundColor: colors.white,
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    width: '100%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
    marginBottom: 20,
  },
  refLabel: { fontSize: 12, fontWeight: '700', color: '#8E8E93', letterSpacing: 1, marginBottom: 8 },
  refDivider: { height: 1, backgroundColor: '#F0F0F5', width: '60%', marginBottom: 12 },
  refFolio: { fontSize: 17, fontWeight: '700', color: '#1A1A1A', marginBottom: 8 },
  refAmountRow: { flexDirection: 'row', alignItems: 'center' },
  refAmount: { fontSize: 18, fontWeight: '700', color: '#22C55E' },
  refDot: { fontSize: 18, color: '#CCC', marginHorizontal: 8 },
  refMethod: { fontSize: 16, color: '#666' },

  notifText: { fontSize: 14, color: '#8E8E93', textAlign: 'center', lineHeight: 20 },

  bottomBar: {
    paddingHorizontal: 16,
    paddingBottom: 24,
    gap: 10,
  },
  btnNext: {
    flexDirection: 'row',
    backgroundColor: colors.primary,
    borderRadius: 14,
    paddingVertical: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  btnNextText: { fontSize: 16, fontWeight: '700', color: colors.white },
  btnNextArrow: { fontSize: 18, color: colors.white, marginLeft: 8 },

  btnProposals: {
    backgroundColor: colors.white,
    borderWidth: 2,
    borderColor: colors.primary,
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: 'center',
  },
  btnProposalsText: { fontSize: 16, fontWeight: '700', color: colors.primary },
});
