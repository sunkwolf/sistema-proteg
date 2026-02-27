/**
 * Ficha del Empleado - Perfil 360 y Configuración
 * 
 * Diseño: Claudy ✨
 * Secciones colapsables para RRHH, Roles y Perfiles Específicos.
 * Creado el 2026-02-27.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  Switch,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { colors, spacing, radius, cardShadow } from '@/theme';
import { formatMoney } from '@/utils/format';

// ─── Components ───────────────────────────────────────────────────────────────

function InfoRow({ label, value, icon }: { label: string; value: string; icon: string }) {
  return (
    <View style={styles.infoRow}>
      <Ionicons name={icon as any} size={18} color={colors.textMedium} style={styles.infoIcon} />
      <View>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text style={styles.infoValue}>{value}</Text>
      </View>
    </View>
  );
}

function SectionCard({ title, icon, children }: { title: string; icon: string; children: React.ReactNode }) {
  return (
    <View style={styles.sectionCard}>
      <View style={styles.sectionHeader}>
        <Ionicons name={icon as any} size={20} color={colors.primary} />
        <Text style={styles.sectionTitle}>{title}</Text>
      </View>
      <View style={styles.sectionContent}>{children}</View>
    </View>
  );
}

// ─── Main Screen ──────────────────────────────────────────────────────────────

export default function EmpleadoDetalleScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams();

  // Mock de datos del empleado (basado en la reestructura Persona -> Rol -> Perfil)
  const [employee] = useState({
    id: id,
    code: 'EMP-001',
    fullName: 'Fernando López',
    rfc: 'LOVF850101XYZ',
    curp: 'LOVF850101HMZLLR01',
    since: '17 de Febrero, 2018',
    email: 'fer@protegrt.com',
    phone: '33 1234 5678',
    status: 'active',
    roles: [
      { id: 'r1', type: 'admin', label: 'Administrador', active: true },
      { id: 'r2', type: 'claims', label: 'Ajustador', active: true },
      { id: 'r3', type: 'sales', label: 'Vendedor', active: true },
    ]
  });

  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <Text style={styles.headerTitle}>Ficha de Empleado</Text>
        <Pressable style={styles.editButton}>
          <Ionicons name="create-outline" size={22} color={colors.white} />
        </Pressable>
      </View>

      <ScrollView style={styles.scroll} showsVerticalScrollIndicator={false}>
        {/* Profile Summary */}
        <View style={styles.profileSummary}>
          <View style={[styles.avatar, { backgroundColor: '#6D28D9' }]}>
            <Text style={styles.avatarText}>FL</Text>
          </View>
          <Text style={styles.profileName}>{employee.fullName}</Text>
          <View style={styles.statusBadge}>
            <View style={styles.statusDot} />
            <Text style={styles.statusText}>EMPLEADO ACTIVO</Text>
          </View>
        </View>

        {/* RRHH Info */}
        <SectionCard title="Información de RRHH" icon="person-circle-outline">
          <InfoRow label="Código" value={employee.code} icon="barcode-outline" />
          <InfoRow label="RFC" value={employee.rfc} icon="document-text-outline" />
          <InfoRow label="CURP" value={employee.curp} icon="id-card-outline" />
          <InfoRow label="Fecha de Ingreso" value={employee.since} icon="calendar-outline" />
          <InfoRow label="Contacto" value={employee.email} icon="mail-outline" />
        </SectionCard>

        {/* Roles Management */}
        <SectionCard title="Roles y Funciones" icon="shield-checkmark-outline">
          {employee.roles.map(role => (
            <View key={role.id} style={styles.roleRow}>
              <View style={styles.roleInfo}>
                <Text style={styles.roleLabel}>{role.label}</Text>
                <Text style={styles.roleSubtext}>Acceso completo al módulo</Text>
              </View>
              <Switch 
                value={role.active} 
                trackColor={{ false: colors.border, true: colors.primaryBg }}
                thumbColor={role.active ? colors.primary : colors.textMedium}
              />
            </View>
          ))}
          <Pressable style={styles.addRoleButton}>
            <Ionicons name="add-circle-outline" size={18} color={colors.primary} />
            <Text style={styles.addRoleText}>Asignar nuevo rol</Text>
          </Pressable>
        </SectionCard>

        {/* Perfil Ajustador (Dynamic) */}
        <SectionCard title="Perfil Ajustador" icon="car-outline">
          <View style={styles.profileStat}>
            <Text style={styles.statLabel}>Cédula Profesional</Text>
            <Text style={styles.statValue}>CED-99283-X</Text>
          </View>
          <View style={styles.profileStat}>
            <Text style={styles.statLabel}>Vehículo Asignado</Text>
            <Text style={styles.statValue}>Nissan March (JAL-22-19)</Text>
          </View>
        </SectionCard>

        {/* Perfil Vendedor (Dynamic) */}
        <SectionCard title="Perfil Vendedor" icon="trending-up-outline">
          <View style={styles.profileStatRow}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Nivel Actual</Text>
              <Text style={[styles.statValue, { color: colors.success }]}>Nivel 7 (Máximo)</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Ventas Mes</Text>
              <Text style={styles.statValue}>48 pólizas</Text>
            </View>
          </View>
          <View style={styles.profileStat}>
            <Text style={styles.statLabel}>Tasa de Comisión</Text>
            <Text style={styles.statValue}>Multinivel Dinámico (V2)</Text>
          </View>
        </SectionCard>

        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.background },
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
  editButton: { width: 40, height: 40, justifyContent: 'center', alignItems: 'flex-end' },
  scroll: { flex: 1 },
  
  profileSummary: {
    alignItems: 'center',
    paddingVertical: spacing['2xl'],
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.md,
    ...cardShadow,
  },
  avatarText: { fontSize: 28, fontWeight: '700', color: colors.white },
  profileName: { fontSize: 22, fontWeight: '700', color: colors.textDark, marginBottom: spacing.xs },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.successBg,
    paddingHorizontal: spacing.md,
    paddingVertical: 4,
    borderRadius: radius.full,
  },
  statusDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.success, marginRight: 6 },
  statusText: { fontSize: 10, fontWeight: '700', color: colors.success },

  sectionCard: {
    backgroundColor: colors.white,
    marginTop: spacing.lg,
    marginHorizontal: spacing.lg,
    borderRadius: radius.lg,
    padding: spacing.lg,
    ...cardShadow,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.lg,
    paddingBottom: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  sectionTitle: { fontSize: 13, fontWeight: '700', color: colors.textMedium, letterSpacing: 0.5, textTransform: 'uppercase' },
  sectionContent: { gap: spacing.md },
  
  infoRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.md, paddingVertical: 2 },
  infoIcon: { width: 24 },
  infoLabel: { fontSize: 10, color: colors.textMedium, textTransform: 'uppercase', letterSpacing: 0.5 },
  infoValue: { fontSize: 15, color: colors.textDark, fontWeight: '500' },
  
  roleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.sm,
  },
  roleInfo: { flex: 1 },
  roleLabel: { fontSize: 15, fontWeight: '600', color: colors.textDark },
  roleSubtext: { fontSize: 12, color: colors.textMedium },
  
  addRoleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  addRoleText: { fontSize: 13, fontWeight: '600', color: colors.primary },
  
  profileStatRow: { flexDirection: 'row', gap: spacing.xl },
  statItem: { flex: 1 },
  profileStat: { marginBottom: spacing.sm },
  statLabel: { fontSize: 11, color: colors.textMedium, marginBottom: 2 },
  statValue: { fontSize: 15, fontWeight: '600', color: colors.textDark },
});
