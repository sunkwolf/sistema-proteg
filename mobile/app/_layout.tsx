import React, { useEffect } from 'react';
import { Slot } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { QueryProvider } from '@/providers/QueryProvider';
import { useAuthStore } from '@/store/auth';

function AuthRestorer({ children }: { children: React.ReactNode }) {
  const restore = useAuthStore((s) => s.restore);

  useEffect(() => {
    restore();
  }, []);

  return <>{children}</>;
}

export default function RootLayout() {
  return (
    <QueryProvider>
      <AuthRestorer>
        <StatusBar style="light" />
        <Slot />
      </AuthRestorer>
    </QueryProvider>
  );
}
