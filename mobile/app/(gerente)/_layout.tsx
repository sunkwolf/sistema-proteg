import React from 'react';
import { Tabs } from 'expo-router';
import { Ionicons, MaterialCommunityIcons, FontAwesome5 } from '@expo/vector-icons';
import { colors } from '@/theme';

export default function GerenteLayout() {
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
        name="propuestas/index"
        options={{
          title: 'Propuestas',
          tabBarIcon: ({ color, size }) => <Ionicons name="clipboard" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="efectivo"
        options={{
          title: 'Efectivo',
          tabBarIcon: ({ color, size }) => <MaterialCommunityIcons name="cash-multiple" size={size} color={color} />,
        }}
      />

      <Tabs.Screen
        name="rutas"
        options={{
          title: 'Rutas',
          tabBarIcon: ({ color, size }) => <MaterialCommunityIcons name="map-marker-path" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="comisiones"
        options={{
          title: 'Comisiones',
          tabBarIcon: ({ color, size }) => <Ionicons name="stats-chart" size={size} color={color} />,
        }}
      />

      {/* Hidden screens */}
      <Tabs.Screen name="propuestas/[id]" options={{ href: null }} />
      <Tabs.Screen name="historial-ruta" options={{ href: null }} />
    </Tabs>
  );
}
