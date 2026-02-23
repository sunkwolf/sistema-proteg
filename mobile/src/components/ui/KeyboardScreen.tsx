import React from 'react';
import { KeyboardAvoidingView, Platform, StyleSheet } from 'react-native';

interface KeyboardScreenProps {
  children: React.ReactNode;
  style?: any;
}

export function KeyboardScreen({ children, style }: KeyboardScreenProps) {
  return (
    <KeyboardAvoidingView
      style={[styles.container, style]}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
    >
      {children}
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
});
