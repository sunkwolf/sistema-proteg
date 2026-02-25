import React from 'react';
import { Tabs } from 'expo-router';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { colors } from '@/theme';

export default function CobradorLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: '#A0A0B0',
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
          tabBarIcon: ({ color, size }) => <Ionicons name="home" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="folios/index"
        options={{
          title: 'Folios',
          tabBarIcon: ({ color, size }) => <Ionicons name="document-text" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="ruta"
        options={{
          title: 'Ruta',
          tabBarIcon: ({ color, size }) => <MaterialCommunityIcons name="map-marker-path" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="propuestas"
        options={{
          title: 'Propuestas',
          tabBarIcon: ({ color, size }) => <Ionicons name="clipboard" size={size} color={color} />,
        }}
      />

      {/* Pantallas modales — ocultas de tabs */}
      <Tabs.Screen name="folios/[folio]" options={{ href: null }} />
      <Tabs.Screen name="cobros/nuevo" options={{ href: null }} />
      <Tabs.Screen name="avisos/nuevo" options={{ href: null }} />
      <Tabs.Screen name="efectivo" options={{ href: null }} />
      <Tabs.Screen name="notificaciones" options={{ href: null }} />
      <Tabs.Screen name="cobros/exito" options={{ href: null }} />
    </Tabs>
  );
}
