import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons, Feather } from '@expo/vector-icons';
import { colors } from '@/theme';

interface ScreenHeaderProps {
  title: string;
  subtitle?: string;
  showBack?: boolean;
  rightIcon?: 'more' | 'settings' | 'help' | 'search';
  onRightPress?: () => void;
}

const RIGHT_ICONS = {
  more: { lib: 'Feather', name: 'more-vertical' },
  settings: { lib: 'Ionicons', name: 'settings-outline' },
  help: { lib: 'Ionicons', name: 'help-circle-outline' },
  search: { lib: 'Feather', name: 'search' },
};

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
          <Ionicons name="chevron-back" size={24} color={colors.white} />
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
          {RIGHT_ICONS[rightIcon].lib === 'Feather' ? (
            <Feather name={RIGHT_ICONS[rightIcon].name as any} size={20} color={colors.white} />
          ) : (
            <Ionicons name={RIGHT_ICONS[rightIcon].name as any} size={22} color={colors.white} />
          )}
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
  titleBlock: { flex: 1, alignItems: 'center' },
  title: { fontSize: 18, fontWeight: '700', color: colors.white },
  subtitle: { fontSize: 13, color: 'rgba(255,255,255,0.8)', marginTop: 1 },
  rightBtn: { width: 40, alignItems: 'flex-end' },
  spacer: { width: 40 },
});
