import React from 'react';
import { View, TextInput, Text, StyleSheet, TextInputProps, ViewStyle } from 'react-native';
import { colors, spacing, radius } from '@/theme';

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  containerStyle?: ViewStyle;
  rightIcon?: React.ReactNode;
  prefix?: string;
}

export function Input({ label, error, containerStyle, rightIcon, prefix, style, ...props }: InputProps) {
  return (
    <View style={[styles.container, containerStyle]}>
      {label && <Text style={styles.label}>{label}</Text>}
      <View style={[styles.inputWrapper, error && styles.inputError]}>
        {prefix && <Text style={styles.prefix}>{prefix}</Text>}
        <TextInput
          style={[styles.input, prefix && { paddingLeft: 0 }, style]}
          placeholderTextColor={colors.textLight}
          {...props}
        />
        {rightIcon && <View style={styles.rightIcon}>{rightIcon}</View>}
      </View>
      {error && <Text style={styles.error}>{error}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.lg,
  },
  label: {
    fontSize: 13,
    fontWeight: '700',
    color: colors.textMedium,
    marginBottom: 6,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8F8FC',
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  inputError: {
    borderColor: colors.error,
  },
  prefix: {
    paddingLeft: spacing.lg,
    fontSize: 16,
    fontWeight: '600',
    color: colors.textDark,
  },
  input: {
    flex: 1,
    height: 50,
    paddingHorizontal: spacing.lg,
    fontSize: 16,
    fontWeight: '400',
    color: colors.textDark,
  },
  rightIcon: {
    paddingRight: spacing.md,
  },
  error: {
    fontSize: 12,
    color: colors.error,
    marginTop: 4,
  },
});
