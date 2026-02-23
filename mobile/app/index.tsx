import React, { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '@/store/auth';
import { colors } from '@/theme';

export default function Index() {
  const router = useRouter();
  const { isLoading, isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    if (isLoading) return;

    if (!isAuthenticated) {
      router.replace('/(auth)/login');
      return;
    }

    if (user?.role === 'gerente_cobranza' || user?.role === 'auxiliar_cobranza') {
      router.replace('/(gerente)');
    } else {
      router.replace('/(cobrador)');
    }
  }, [isLoading, isAuthenticated, user?.role]);

  return (
    <View style={styles.center}>
      <ActivityIndicator size="large" color={colors.primary} />
    </View>
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
});
