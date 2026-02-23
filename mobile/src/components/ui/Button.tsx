import React from 'react';
import { Pressable, Text, StyleSheet, ActivityIndicator, ViewStyle, TextStyle } from 'react-native';
import { colors, spacing, radius, typography } from '@/theme';

type ButtonVariant = 'primary' | 'success' | 'danger' | 'secondary' | 'ghost';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  icon?: string;
  loading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
  size?: 'sm' | 'md' | 'lg';
}

const variantStyles: Record<ButtonVariant, { bg: string; text: string }> = {
  primary: { bg: colors.primary, text: colors.white },
  success: { bg: colors.success, text: colors.white },
  danger: { bg: colors.danger, text: colors.white },
  secondary: { bg: colors.gray100, text: colors.gray800 },
  ghost: { bg: 'transparent', text: colors.primary },
};

const sizeStyles: Record<string, { height: number; fontSize: number }> = {
  sm: { height: 36, fontSize: 14 },
  md: { height: 48, fontSize: 16 },
  lg: { height: 56, fontSize: 18 },
};

export function Button({
  title,
  onPress,
  variant = 'primary',
  icon,
  loading = false,
  disabled = false,
  style,
  size = 'md',
}: ButtonProps) {
  const v = variantStyles[variant];
  const s = sizeStyles[size];

  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || loading}
      style={({ pressed }) => [
        styles.base,
        {
          backgroundColor: v.bg,
          height: s.height,
          opacity: disabled ? 0.5 : pressed ? 0.85 : 1,
        },
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={v.text} />
      ) : (
        <Text style={[styles.text, { color: v.text, fontSize: s.fontSize }]}>
          {icon ? `${icon}  ${title}` : title}
        </Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: radius.md,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.xl,
  },
  text: {
    fontWeight: '600',
  },
});
