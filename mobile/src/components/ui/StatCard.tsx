import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, radius, cardShadow } from '@/theme';

interface StatCardProps {
  icon: string;
  iconBg: string;
  iconColor?: string;
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
    width: '48%',
    backgroundColor: colors.white,
    borderRadius: radius.lg,
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 12,
    ...cardShadow,
  },
  top: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconBox: {
    width: 40,
    height: 40,
    borderRadius: radius.md,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconText: {
    fontSize: 18,
  },
  label: {
    fontSize: 13,
    fontWeight: '400',
    color: colors.textMedium,
    marginLeft: 8,
    flex: 1,
  },
  value: {
    fontSize: 22,
    fontWeight: '800',
    color: colors.textDark,
    marginTop: 10,
  },
});
