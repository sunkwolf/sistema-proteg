import React from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';
import { colors, spacing, radius, cardShadow } from '@/theme';

const CARD_WIDTH = (Dimensions.get('window').width - 32 - 12) / 2; // 32 = 16px padding each side, 12 = gap

interface StatCardProps {
  icon: string;
  iconBg: string;
  iconColor: string;
  label: string;
  value: string;
}

export function StatCard({ icon, iconBg, label, value }: StatCardProps) {
  return (
    <View style={styles.card}>
      <View style={styles.top}>
        <View style={[styles.iconBox, { backgroundColor: iconBg }]}>
          <Text style={styles.iconText}>{icon}</Text>
        </View>
        <Text style={styles.label}>{label}</Text>
      </View>
      <Text style={styles.value} numberOfLines={1} adjustsFontSizeToFit>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    width: CARD_WIDTH,
    backgroundColor: colors.white,
    borderRadius: radius.lg,
    paddingHorizontal: 18,
    paddingVertical: 18,
    borderWidth: 1,
    borderColor: colors.border,
    ...cardShadow,
  },
  top: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconBox: {
    width: 44,
    height: 44,
    borderRadius: radius.md,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconText: {
    fontSize: 20,
  },
  label: {
    fontSize: 13,
    fontWeight: '400',
    color: colors.textMedium,
    marginLeft: 10,
    flex: 1,
  },
  value: {
    fontSize: 22,
    fontWeight: '800',
    color: colors.textDark,
    marginTop: 12,
  },
});
