import React from 'react';
import { Tabs } from 'expo-router';
import { Text, View, StyleSheet } from 'react-native';
import { colors } from '@/theme';

function TabIcon({ emoji, focused }: { emoji: string; focused: boolean }) {
  return <Text style={{ fontSize: 24, opacity: focused ? 1 : 0.45 }}>{emoji}</Text>;
}

export default function CobradorLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false, // Cada pantalla maneja su propio header
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textLight,
        tabBarStyle: {
          backgroundColor: colors.white,
          borderTopWidth: 1,
          borderTopColor: colors.border,
          height: 64,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarLabelStyle: { fontSize: 11, fontWeight: '500' },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Inicio',
          tabBarIcon: ({ focused }) => <TabIcon emoji="🏠" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="folios/index"
        options={{
          title: 'Folios',
          tabBarIcon: ({ focused }) => <TabIcon emoji="📋" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="ruta"
        options={{
          title: 'Ruta',
          tabBarIcon: ({ focused }) => <TabIcon emoji="🗺️" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="propuestas"
        options={{
          title: 'Propuestas',
          tabBarIcon: ({ focused }) => <TabIcon emoji="📊" focused={focused} />,
        }}
      />

      {/* Pantallas modales — ocultas de tabs */}
      <Tabs.Screen name="folios/[folio]" options={{ href: null }} />
      <Tabs.Screen name="cobros/nuevo" options={{ href: null }} />
      <Tabs.Screen name="cobros/abono" options={{ href: null }} />
      <Tabs.Screen name="avisos/nuevo" options={{ href: null }} />
      <Tabs.Screen name="efectivo" options={{ href: null }} />
      <Tabs.Screen name="notificaciones" options={{ href: null }} />
    </Tabs>
  );
}
