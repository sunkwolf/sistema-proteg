import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { colors } from '@/theme';

interface Notification {
  id: string;
  type: 'approved' | 'rejected' | 'info' | 'warning';
  title: string;
  body: string;
  time: string;
  unread: boolean;
  actionText?: string;
}

const ICON_CONFIG: Record<string, { bg: string; icon: string }> = {
  approved: { bg: '#4CAF50', icon: '✓' },
  rejected: { bg: '#FFCDD2', icon: '✗' },
  info: { bg: '#42A5F5', icon: 'i' },
  warning: { bg: '#FFA726', icon: '⚠' },
};

const MOCK_NOTIFICATIONS: { section: string; items: Notification[] }[] = [
  {
    section: 'HOY',
    items: [
      { id: '1', type: 'approved', title: 'Pago aprobado - F:18405', body: '$1,200 Pago #3 aprobado por Elena', time: '2h', unread: false },
      { id: '2', type: 'rejected', title: 'Pago rechazado - F:18615', body: 'Motivo: Recibo incorrecto.', time: '3h', unread: true, actionText: 'Toca para corregir' },
      { id: '3', type: 'info', title: 'Tarjeta asignada', body: 'Se te asignó nueva cuenta F:18900 Carmen Ruiz', time: '4h', unread: false },
    ],
  },
  {
    section: 'AYER',
    items: [
      { id: '4', type: 'warning', title: 'Efectivo acumulado', body: 'Tienes $4,800 sin depositar. Entrega tu efectivo.', time: 'Ayer', unread: false },
      { id: '5', type: 'approved', title: 'Pago aprobado - F:18310', body: '$1,200 aprobado', time: 'Ayer', unread: false },
    ],
  },
];

export default function NotificacionesScreen() {
  const router = useRouter();

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={{ width: 40 }}>
          <Text style={styles.backArrow}>←</Text>
        </Pressable>
        <Text style={styles.headerTitle}>Notificaciones</Text>
        <Pressable style={{ width: 40, alignItems: 'flex-end' }}>
          <Text style={{ color: colors.white, fontSize: 20 }}>⚙</Text>
        </Pressable>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scroll}>
        {MOCK_NOTIFICATIONS.map(group => (
          <View key={group.section}>
            <Text style={styles.sectionHeader}>{group.section}</Text>
            {group.items.map(n => {
              const cfg = ICON_CONFIG[n.type];
              return (
                <Pressable key={n.id} style={styles.notifCard}>
                  {/* Icon */}
                  <View style={styles.iconWrapper}>
                    <View style={[styles.iconCircle, { backgroundColor: cfg.bg }]}>
                      <Text style={[
                        styles.iconText,
                        n.type === 'rejected' && { color: '#FF3B30' },
                      ]}>
                        {cfg.icon}
                      </Text>
                    </View>
                    {n.unread && <View style={styles.unreadDot} />}
                  </View>

                  {/* Content */}
                  <View style={styles.notifContent}>
                    <Text style={styles.notifTitle}>{n.title}</Text>
                    <Text style={styles.notifBody}>
                      {n.body}
                      {n.actionText && (
                        <Text style={styles.actionLink}> {n.actionText}</Text>
                      )}
                    </Text>
                  </View>

                  {/* Time + chevron */}
                  <View style={styles.notifRight}>
                    <Text style={styles.notifTime}>{n.time}</Text>
                    {n.type === 'rejected' && (
                      <Text style={styles.chevron}>›</Text>
                    )}
                  </View>
                </Pressable>
              );
            })}
          </View>
        ))}

        <Text style={styles.endText}>No hay más notificaciones</Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.primary },

  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    backgroundColor: colors.primary,
  },
  backArrow: { fontSize: 22, color: colors.white, fontWeight: '600' },
  headerTitle: { fontSize: 20, fontWeight: '700', color: colors.white },

  scrollView: { flex: 1, backgroundColor: colors.background },
  scroll: { paddingBottom: 40 },

  sectionHeader: {
    fontSize: 13,
    fontWeight: '700',
    color: '#666',
    letterSpacing: 0.5,
    paddingHorizontal: 16,
    paddingTop: 20,
    paddingBottom: 10,
  },

  notifCard: {
    flexDirection: 'row',
    backgroundColor: colors.white,
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F5',
  },

  iconWrapper: { position: 'relative', marginRight: 12 },
  iconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconText: { fontSize: 18, fontWeight: '700', color: colors.white },
  unreadDot: {
    position: 'absolute',
    top: -2,
    right: -2,
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#FF3B30',
    borderWidth: 2,
    borderColor: colors.white,
  },

  notifContent: { flex: 1, marginRight: 8 },
  notifTitle: { fontSize: 15, fontWeight: '700', color: '#1A1A2E', marginBottom: 4 },
  notifBody: { fontSize: 13, color: '#4A4A5A', lineHeight: 18 },
  actionLink: { color: colors.primary, fontWeight: '500' },

  notifRight: { alignItems: 'flex-end', justifyContent: 'flex-start' },
  notifTime: { fontSize: 12, color: '#9E9E9E' },
  chevron: { fontSize: 24, color: '#CCC', marginTop: 4 },

  endText: {
    textAlign: 'center',
    color: '#8E8E9A',
    fontSize: 13,
    marginTop: 32,
  },
});
