import React, { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { Redirect, useRouter } from 'expo-router';
import { useAuthStore } from '@/store/auth';
import { colors } from '@/theme';

export default function Index() {
  const { isLoading, isAuthenticated, user } = useAuthStore();

  // Still loading auth state from storage
  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  // Not authenticated — go to login
  if (!isAuthenticated) {
    return <Redirect href="/(auth)/login" />;
  }

  // Authenticated — route by role
  if (user?.role === 'gerente_cobranza' || user?.role === 'auxiliar_cobranza') {
    return <Redirect href="/(gerente)" />;
  }

  return <Redirect href="/(cobrador)" />;
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
});
