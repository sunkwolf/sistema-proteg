import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { colors, spacing, typography } from '@/theme';

interface SectionHeaderProps {
  title: string;
  actionText?: string;
  onAction?: () => void;
}

/** Título de sección con barra lateral azul (patrón Stitch) */
export function SectionHeader({ title, actionText, onAction }: SectionHeaderProps) {
  return (
    <View style={styles.container}>
      <View style={styles.left}>
        <View style={styles.accent} />
        <Text style={typography.sectionTitle}>{title}</Text>
      </View>
      {actionText && onAction && (
        <Pressable onPress={onAction}>
          <Text style={styles.action}>{actionText} →</Text>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 28,
    marginBottom: 16,
  },
  left: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  accent: {
    width: 4,
    height: 22,
    borderRadius: 2,
    backgroundColor: colors.primary,
    marginRight: 10,
  },
  action: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.primary,
  },
});
