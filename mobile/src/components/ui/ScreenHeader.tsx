import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import { colors } from '@/theme';

interface ScreenHeaderProps {
  title: string;
  subtitle?: string;
  showBack?: boolean;
  rightIcon?: string;
  onRightPress?: () => void;
}

export function ScreenHeader({
  title,
  subtitle,
  showBack = true,
  rightIcon,
  onRightPress,
}: ScreenHeaderProps) {
  const router = useRouter();

  return (
    <View style={styles.header}>
      {showBack ? (
        <Pressable onPress={() => router.back()} style={styles.backBtn} hitSlop={8}>
          <Text style={styles.backArrow}>←</Text>
        </Pressable>
      ) : (
        <View style={styles.spacer} />
      )}

      <View style={styles.titleBlock}>
        <Text style={styles.title} numberOfLines={1}>{title}</Text>
        {subtitle && <Text style={styles.subtitle} numberOfLines={1}>{subtitle}</Text>}
      </View>

      {rightIcon ? (
        <Pressable onPress={onRightPress} style={styles.rightBtn} hitSlop={8}>
          <Text style={styles.rightIcon}>{rightIcon}</Text>
        </Pressable>
      ) : (
        <View style={styles.spacer} />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primary,
    paddingHorizontal: 16,
    paddingVertical: 14,
    minHeight: 56,
  },
  backBtn: { width: 40, alignItems: 'flex-start' },
  backArrow: { fontSize: 22, color: colors.white, fontWeight: '600' },
  titleBlock: { flex: 1, alignItems: 'center' },
  title: { fontSize: 18, fontWeight: '700', color: colors.white },
  subtitle: { fontSize: 13, color: 'rgba(255,255,255,0.8)', marginTop: 1 },
  rightBtn: { width: 40, alignItems: 'flex-end' },
  rightIcon: { fontSize: 20, color: colors.white },
  spacer: { width: 40 },
});
