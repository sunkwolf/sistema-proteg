/**
 * Lista de Empleados - Gestión centralizada del equipo
 * 
 * Diseño: Claudy ✨
 * Vista de cartas con badges de roles y buscador.
 * Creado el 2026-02-27.
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  Pressable,
  TextInput,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { colors, spacing, radius, cardShadow } from '@/theme';

// ─── Types ────────────────────────────────────────────────────────────────────

type EmployeeRoleType = 'sales' | 'collection' | 'claims' | 'admin';

interface EmployeeSummary {
  id: string;
  code: string;
  fullName: string;
  initials: string;
  avatarColor: string;
  status: 'active' | 'inactive';
  roles: EmployeeRoleType[];
  since: string;
}

// ─── Constants & Helpers ──────────────────────────────────────────────────────

const AVATAR_COLORS = [
  '#6D28D9', '#D97706', '#4F46E5', '#059669',
  '#DC2626', '#2563EB', '#7C3AED', '#DB2777',
];

const ROLE_LABELS: Record<EmployeeRoleType, { label: string; color: string; icon: string }> = {
  sales: { label: 'Vendedor', color: '#10B981', icon: 'cart-outline' },
  collection: { label: 'Cobrador', color: '#3B82F6', icon: 'wallet-outline' },
  claims: { label: 'Ajustador', color: '#F59E0B', icon: 'shield-checkmark-outline' },
  admin: { label: 'Admin', color: '#6D28D9', icon: 'settings-outline' },
};

// ─── Components ───────────────────────────────────────────────────────────────

function RoleBadge({ type }: { type: EmployeeRoleType }) {
  const config = ROLE_LABELS[type];
  return (
    <View style={[styles.roleBadge, { backgroundColor: config.color + '15', borderColor: config.color }]}>
      <Ionicons name={config.icon as any} size={10} color={config.color} />
      <Text style={[styles.roleText, { color: config.color }]}>{config.label}</Text>
    </View>
  );
}

function EmployeeCard({ item, onPress }: { item: EmployeeSummary; onPress: () => void }) {
  return (
    <Pressable 
      style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
      onPress={onPress}
    >
      <View style={styles.cardHeader}>
        <View style={[styles.avatar, { backgroundColor: item.avatarColor }]}>
          <Text style={styles.avatarText}>{item.initials}</Text>
        </View>
        <View style={styles.cardInfo}>
          <Text style={styles.cardName}>{item.fullName}</Text>
          <Text style={styles.cardCode}>{item.code} · Ingreso: {item.since}</Text>
        </View>
        <Ionicons name="chevron-forward" size={20} color={colors.textMedium} />
      </View>
      
      <View style={styles.rolesContainer}>
        {item.roles.map(role => (
          <RoleBadge key={role} type={role} />
        ))}
      </View>
    </Pressable>
  );
}

// ─── Main Screen ──────────────────────────────────────────────────────────────

export default function EmpleadosListScreen() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false); // Cambiar a true cuando conectemos API

  // Mocks iniciales para pintar el diseño
  const [empleados] = useState<EmployeeSummary[]>([
    {
      id: '1',
      code: 'EMP-001',
      fullName: 'Fernando López',
      initials: 'FL',
      avatarColor: AVATAR_COLORS[0],
      status: 'active',
      roles: ['admin', 'claims', 'sales'],
      since: '2018',
    },
    {
      id: '2',
      code: 'EMP-002',
      fullName: 'Edgar Ramírez',
      initials: 'ER',
      avatarColor: AVATAR_COLORS[1],
      status: 'active',
      roles: ['collection'],
      since: '2020',
    },
    {
      id: '3',
      code: 'EMP-003',
      fullName: 'Gabriela López',
      initials: 'GL',
      avatarColor: AVATAR_COLORS[2],
      status: 'active',
      roles: ['sales', 'admin'],
      since: '2019',
    },
  ]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1000);
  }, []);

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <Text style={styles.headerTitle}>Equipo Proteg-rt</Text>
        <Pressable style={styles.addButton}>
          <Ionicons name="person-add-outline" size={22} color={colors.white} />
        </Pressable>
      </View>

      {/* Search Bar */}
      <View style={styles.searchSection}>
        <View style={styles.searchContainer}>
          <Ionicons name="search-outline" size={20} color={colors.textMedium} />
          <TextInput
            style={styles.searchInput}
            placeholder="Buscar por nombre o código..."
            placeholderTextColor={colors.textMedium}
            value={search}
            onChangeText={setSearch}
          />
          {search.length > 0 && (
            <Pressable onPress={() => setSearch('')}>
              <Ionicons name="close-circle" size={18} color={colors.textMedium} />
            </Pressable>
          )}
        </View>
      </View>

      {/* List */}
      <FlatList
        data={empleados}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <EmployeeCard 
            item={item} 
            onPress={() => router.push(`/(gerente)/empleados/${item.id}`)} 
          />
        )}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="people-outline" size={48} color={colors.textMedium} />
            <Text style={styles.emptyText}>No se encontraron empleados</Text>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  backButton: { width: 40, height: 40, justifyContent: 'center' },
  headerTitle: {
    flex: 1,
    fontSize: 18,
    fontWeight: '700',
    color: colors.white,
    textAlign: 'center',
  },
  addButton: { width: 40, height: 40, justifyContent: 'center', alignItems: 'flex-end' },
  
  searchSection: {
    padding: spacing.lg,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    gap: spacing.sm,
  },
  searchInput: {
    flex: 1,
    fontSize: 15,
    color: colors.textDark,
    paddingVertical: Platform.OS === 'ios' ? spacing.xs : 0,
  },
  
  listContent: {
    padding: spacing.lg,
  },
  card: {
    backgroundColor: colors.white,
    borderRadius: radius.lg,
    padding: spacing.lg,
    marginBottom: spacing.md,
    ...cardShadow,
  },
  cardPressed: {
    opacity: 0.9,
    transform: [{ scale: 0.98 }],
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.white,
  },
  cardInfo: {
    flex: 1,
    marginLeft: spacing.md,
  },
  cardName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textDark,
    marginBottom: 2,
  },
  cardCode: {
    fontSize: 12,
    color: colors.textMedium,
  },
  
  rolesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: spacing.md,
    gap: spacing.xs,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  roleBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: radius.full,
    borderWidth: 1,
    gap: 4,
  },
  roleText: {
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: spacing['3xl'],
    gap: spacing.md,
  },
  emptyText: {
    fontSize: 14,
    color: colors.textMedium,
  },
});
