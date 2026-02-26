/**
 * Detalle de Liquidación - Vista individual de un cobrador
 * 
 * Diseño: Claudy ✨
 * Desglose completo + botón de pago que se siente bien.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  Modal,
  Animated,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { colors, spacing, radius, cardShadow } from '@/theme';
import { formatMoney } from '@/utils/format';

// ─── Types ────────────────────────────────────────────────────────────────────

interface CobroDetalle {
  id: string;
  folio: string;
  cliente: string;
  monto: number;
  tipo: 'normal' | 'contado' | 'entrega';
  comision: number;
  fecha: string;
}

interface DeduccionDetalle {
  id: string;
  concepto: string;
  descripcion: string;
  monto: number;
  tipo: 'gasolina' | 'prestamo' | 'diferencia';
}

interface LiquidacionHistorial {
  id: string;
  periodo: string;
  monto: number;
  status: 'pagado' | 'pendiente';
  fecha?: string;
}

// ─── Mock Data ────────────────────────────────────────────────────────────────

const COBRADOR_MOCK = {
  id: '1',
  nombre: 'Edgar Martínez',
  initials: 'EM',
  avatarColor: '#4A3AFF',
  nivel: 1,
  antiguedad: '2 años',
  metaCobro: 17000,
  totalCobrado: 13200,
  porcentajeMeta: 78,
};

const COMISIONES_MOCK = {
  cobranza: {
    cantidad: 12,
    montoCobrado: 13200,
    porcentaje: 10,
    comision: 1320,
  },
  contado: {
    cantidad: 3,
    montoCobrado: 8500,
    porcentaje: 5,
    comision: 425,
  },
  entregas: {
    cantidad: 5,
    montoUnitario: 50,
    comision: 250,
  },
  total: 1995,
};

const DEDUCCIONES_MOCK: DeduccionDetalle[] = [
  {
    id: '1',
    concepto: 'Gasolina (50%)',
    descripcion: '6 cargas · $800 total',
    monto: 400,
    tipo: 'gasolina',
  },
  {
    id: '2',
    concepto: 'Préstamo moto',
    descripcion: 'Cuota 4 de 12',
    monto: 200,
    tipo: 'prestamo',
  },
];

const HISTORIAL_MOCK: LiquidacionHistorial[] = [
  { id: '1', periodo: '1ra Qna Feb 2026', monto: 1180, status: 'pagado', fecha: '16 feb' },
  { id: '2', periodo: '2da Qna Ene 2026', monto: 1450, status: 'pagado', fecha: '31 ene' },
  { id: '3', periodo: '1ra Qna Ene 2026', monto: 980, status: 'pagado', fecha: '16 ene' },
];

// ─── Components ───────────────────────────────────────────────────────────────

function Section({ 
  title, 
  total, 
  totalColor = colors.textDark,
  icon,
  children,
  defaultExpanded = true,
}: { 
  title: string; 
  total?: number; 
  totalColor?: string;
  icon?: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
}) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  
  return (
    <View style={styles.section}>
      <Pressable style={styles.sectionHeader} onPress={() => setExpanded(!expanded)}>
        <View style={styles.sectionTitleRow}>
          {icon && <Text style={styles.sectionIcon}>{icon}</Text>}
          <Text style={styles.sectionTitle}>{title}</Text>
        </View>
        <View style={styles.sectionRight}>
          {total !== undefined && (
            <Text style={[styles.sectionTotal, { color: totalColor }]}>
              {total >= 0 ? '+' : ''}{formatMoney(total)}
            </Text>
          )}
          <Ionicons 
            name={expanded ? 'chevron-up' : 'chevron-down'} 
            size={18} 
            color={colors.textMedium} 
          />
        </View>
      </Pressable>
      
      {expanded && (
        <View style={styles.sectionContent}>
          {children}
        </View>
      )}
    </View>
  );
}

function ComisionRow({ 
  label, 
  detail, 
  amount, 
  isLast = false 
}: { 
  label: string; 
  detail: string; 
  amount: number; 
  isLast?: boolean;
}) {
  return (
    <View style={[styles.comisionRow, !isLast && styles.comisionRowBorder]}>
      <View style={styles.comisionInfo}>
        <Text style={styles.comisionLabel}>{label}</Text>
        <Text style={styles.comisionDetail}>{detail}</Text>
      </View>
      <Text style={styles.comisionAmount}>+{formatMoney(amount)}</Text>
    </View>
  );
}

function DeduccionRow({ item, isLast = false }: { item: DeduccionDetalle; isLast?: boolean }) {
  const iconMap = {
    gasolina: '⛽',
    prestamo: '🏍️',
    diferencia: '⚠️',
  };
  
  return (
    <View style={[styles.comisionRow, !isLast && styles.comisionRowBorder]}>
      <View style={styles.comisionInfo}>
        <Text style={styles.comisionLabel}>
          {iconMap[item.tipo]} {item.concepto}
        </Text>
        <Text style={styles.comisionDetail}>{item.descripcion}</Text>
      </View>
      <Text style={[styles.comisionAmount, styles.deduccionAmount]}>
        -{formatMoney(item.monto)}
      </Text>
    </View>
  );
}

function PaymentModal({ 
  visible, 
  onClose, 
  onConfirm,
  cobrador,
  neto,
}: { 
  visible: boolean; 
  onClose: () => void; 
  onConfirm: (method: string) => void;
  cobrador: { nombre: string; initials: string; avatarColor: string };
  neto: number;
}) {
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null);
  const [confirming, setConfirming] = useState(false);
  const [success, setSuccess] = useState(false);
  
  const handleConfirm = () => {
    if (!selectedMethod) return;
    setConfirming(true);
    
    // Simular proceso
    setTimeout(() => {
      setSuccess(true);
      setTimeout(() => {
        onConfirm(selectedMethod);
        setSuccess(false);
        setConfirming(false);
        setSelectedMethod(null);
      }, 1500);
    }, 500);
  };
  
  const handleClose = () => {
    setSelectedMethod(null);
    setSuccess(false);
    setConfirming(false);
    onClose();
  };
  
  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={handleClose}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          {success ? (
            // Success state
            <View style={styles.successContainer}>
              <View style={styles.successIcon}>
                <Ionicons name="checkmark" size={48} color={colors.white} />
              </View>
              <Text style={styles.successTitle}>¡Pago registrado!</Text>
              <Text style={styles.successSubtitle}>
                {cobrador.nombre} · {formatMoney(neto)}
              </Text>
            </View>
          ) : (
            // Payment selection
            <>
              <View style={[styles.modalAvatar, { backgroundColor: cobrador.avatarColor }]}>
                <Text style={styles.modalAvatarText}>{cobrador.initials}</Text>
              </View>
              
              <Text style={styles.modalName}>{cobrador.nombre}</Text>
              <Text style={styles.modalAmount}>{formatMoney(neto)}</Text>
              <Text style={styles.modalPeriodo}>2da Quincena · Feb 2026</Text>
              
              <View style={styles.methodsContainer}>
                <Pressable 
                  style={[
                    styles.methodButton,
                    selectedMethod === 'efectivo' && styles.methodSelected,
                  ]}
                  onPress={() => setSelectedMethod('efectivo')}
                >
                  <Ionicons 
                    name="cash-outline" 
                    size={24} 
                    color={selectedMethod === 'efectivo' ? colors.primary : colors.textMedium} 
                  />
                  <Text style={[
                    styles.methodText,
                    selectedMethod === 'efectivo' && styles.methodTextSelected,
                  ]}>Efectivo</Text>
                </Pressable>
                
                <Pressable 
                  style={[
                    styles.methodButton,
                    selectedMethod === 'transferencia' && styles.methodSelected,
                  ]}
                  onPress={() => setSelectedMethod('transferencia')}
                >
                  <Ionicons 
                    name="phone-portrait-outline" 
                    size={24} 
                    color={selectedMethod === 'transferencia' ? colors.primary : colors.textMedium} 
                  />
                  <Text style={[
                    styles.methodText,
                    selectedMethod === 'transferencia' && styles.methodTextSelected,
                  ]}>Transferencia</Text>
                </Pressable>
              </View>
              
              <Pressable 
                style={[
                  styles.confirmButton,
                  !selectedMethod && styles.confirmButtonDisabled,
                ]}
                onPress={handleConfirm}
                disabled={!selectedMethod || confirming}
              >
                {confirming ? (
                  <Text style={styles.confirmButtonText}>Procesando...</Text>
                ) : (
                  <>
                    <Ionicons name="checkmark-circle" size={20} color={colors.white} />
                    <Text style={styles.confirmButtonText}>CONFIRMAR PAGO</Text>
                  </>
                )}
              </Pressable>
              
              <Pressable style={styles.cancelButton} onPress={handleClose}>
                <Text style={styles.cancelButtonText}>Cancelar</Text>
              </Pressable>
            </>
          )}
        </View>
      </View>
    </Modal>
  );
}

// ─── Main Screen ──────────────────────────────────────────────────────────────

export default function LiquidacionDetalleScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams();
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  
  // Mock data - en producción vendría del API
  const cobrador = COBRADOR_MOCK;
  const comisiones = COMISIONES_MOCK;
  const deducciones = DEDUCCIONES_MOCK;
  const historial = HISTORIAL_MOCK;
  
  const totalDeducciones = deducciones.reduce((sum, d) => sum + d.monto, 0);
  const neto = comisiones.total - totalDeducciones;
  
  const handlePaymentConfirm = (method: string) => {
    console.log(`Pago confirmado: ${method}`);
    setShowPaymentModal(false);
    // TODO: Navegar de vuelta con estado actualizado
    router.back();
  };
  
  return (
    <SafeAreaView edges={['top']} style={styles.safe}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="chevron-back" size={24} color={colors.white} />
        </Pressable>
        <Text style={styles.headerTitle}>{cobrador.nombre}</Text>
        <Pressable style={styles.moreButton}>
          <Ionicons name="ellipsis-horizontal" size={22} color={colors.white} />
        </Pressable>
      </View>
      
      <ScrollView style={styles.scroll} showsVerticalScrollIndicator={false}>
        {/* Profile card */}
        <View style={styles.profileCard}>
          <View style={[styles.avatar, { backgroundColor: cobrador.avatarColor }]}>
            <Text style={styles.avatarText}>{cobrador.initials}</Text>
          </View>
          <Text style={styles.profileName}>{cobrador.nombre}</Text>
          <Text style={styles.profileInfo}>
            Cobrador · Nivel {cobrador.nivel} · {cobrador.antiguedad}
          </Text>
          
          {/* Progress */}
          <View style={styles.progressSection}>
            <View style={styles.progressBar}>
              <View 
                style={[
                  styles.progressFill, 
                  { width: `${Math.min(cobrador.porcentajeMeta, 100)}%` }
                ]} 
              />
            </View>
            <Text style={styles.progressText}>
              {formatMoney(cobrador.totalCobrado)} de {formatMoney(cobrador.metaCobro)} meta
            </Text>
          </View>
        </View>
        
        {/* Neto card */}
        <View style={styles.netoCard}>
          <Text style={styles.netoLabel}>NETO A PAGAR</Text>
          <Text style={[styles.netoValue, neto < 0 && styles.netoNegative]}>
            {formatMoney(neto)}
          </Text>
          
          <Pressable 
            style={styles.payButton}
            onPress={() => setShowPaymentModal(true)}
          >
            <Ionicons name="card-outline" size={20} color={colors.white} />
            <Text style={styles.payButtonText}>PAGAR AHORA</Text>
          </Pressable>
        </View>
        
        {/* Comisiones section */}
        <Section title="COMISIONES" total={comisiones.total} totalColor={colors.success} icon="💰">
          <ComisionRow 
            label="Cobranza normal (10%)"
            detail={`${comisiones.cobranza.cantidad} cobros · ${formatMoney(comisiones.cobranza.montoCobrado)}`}
            amount={comisiones.cobranza.comision}
          />
          <ComisionRow 
            label="Pagos de contado (5%)"
            detail={`${comisiones.contado.cantidad} cobros · ${formatMoney(comisiones.contado.montoCobrado)}`}
            amount={comisiones.contado.comision}
          />
          <ComisionRow 
            label="Entregas ($50 c/u)"
            detail={`${comisiones.entregas.cantidad} pólizas/endosos`}
            amount={comisiones.entregas.comision}
            isLast
          />
          
          <Pressable style={styles.viewAllLink}>
            <Text style={styles.viewAllText}>Ver {comisiones.cobranza.cantidad + comisiones.contado.cantidad} cobros del período</Text>
            <Ionicons name="chevron-forward" size={16} color={colors.primary} />
          </Pressable>
        </Section>
        
        {/* Deducciones section */}
        <Section 
          title="DEDUCCIONES" 
          total={-totalDeducciones} 
          totalColor={colors.error} 
          icon="📉"
        >
          {deducciones.map((item, index) => (
            <DeduccionRow 
              key={item.id} 
              item={item} 
              isLast={index === deducciones.length - 1}
            />
          ))}
          
          {deducciones.length === 0 && (
            <View style={styles.emptyState}>
              <Ionicons name="checkmark-circle" size={24} color={colors.success} />
              <Text style={styles.emptyText}>Sin deducciones este período ✓</Text>
            </View>
          )}
          
          <Pressable style={styles.addDeduccionLink}>
            <Ionicons name="add-circle-outline" size={18} color={colors.primary} />
            <Text style={styles.addDeduccionText}>Agregar deducción manual</Text>
          </Pressable>
        </Section>
        
        {/* Historial section */}
        <Section title="HISTORIAL" icon="📜" defaultExpanded={false}>
          {historial.map((item) => (
            <View key={item.id} style={styles.historialRow}>
              <View>
                <Text style={styles.historialPeriodo}>{item.periodo}</Text>
                {item.fecha && (
                  <Text style={styles.historialFecha}>Pagado el {item.fecha}</Text>
                )}
              </View>
              <View style={styles.historialRight}>
                <Text style={styles.historialMonto}>{formatMoney(item.monto)}</Text>
                <Ionicons 
                  name={item.status === 'pagado' ? 'checkmark-circle' : 'time-outline'} 
                  size={16} 
                  color={item.status === 'pagado' ? colors.success : colors.orange} 
                />
              </View>
            </View>
          ))}
          
          <Pressable style={styles.viewAllLink}>
            <Text style={styles.viewAllText}>Ver historial completo</Text>
            <Ionicons name="chevron-forward" size={16} color={colors.primary} />
          </Pressable>
        </Section>
        
        <View style={{ height: 40 }} />
      </ScrollView>
      
      {/* Payment Modal */}
      <PaymentModal
        visible={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        onConfirm={handlePaymentConfirm}
        cobrador={cobrador}
        neto={neto}
      />
    </SafeAreaView>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.background,
  },
  
  // Header
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
  },
  headerTitle: {
    flex: 1,
    fontSize: 18,
    fontWeight: '700',
    color: colors.white,
    textAlign: 'center',
  },
  moreButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'flex-end',
  },
  
  scroll: {
    flex: 1,
  },
  
  // Profile card
  profileCard: {
    backgroundColor: colors.white,
    margin: spacing.lg,
    padding: spacing.xl,
    borderRadius: radius.lg,
    alignItems: 'center',
    ...cardShadow,
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  avatarText: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.white,
  },
  profileName: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.textDark,
    marginBottom: 4,
  },
  profileInfo: {
    fontSize: 13,
    color: colors.textMedium,
    marginBottom: spacing.lg,
  },
  progressSection: {
    width: '100%',
  },
  progressBar: {
    height: 8,
    backgroundColor: colors.border,
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: spacing.sm,
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 4,
  },
  progressText: {
    fontSize: 12,
    color: colors.textMedium,
    textAlign: 'center',
  },
  
  // Neto card
  netoCard: {
    backgroundColor: colors.white,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    padding: spacing.xl,
    borderRadius: radius.lg,
    alignItems: 'center',
    ...cardShadow,
  },
  netoLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: colors.textMedium,
    letterSpacing: 0.5,
    marginBottom: spacing.sm,
  },
  netoValue: {
    fontSize: 36,
    fontWeight: '700',
    color: colors.primary,
    marginBottom: spacing.lg,
  },
  netoNegative: {
    color: colors.error,
  },
  payButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing['2xl'],
    borderRadius: radius.md,
    gap: spacing.sm,
    width: '100%',
  },
  payButtonText: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.white,
  },
  
  // Sections
  section: {
    backgroundColor: colors.white,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    borderRadius: radius.lg,
    overflow: 'hidden',
    ...cardShadow,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  sectionTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  sectionIcon: {
    fontSize: 16,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: colors.textMedium,
    letterSpacing: 0.5,
  },
  sectionRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  sectionTotal: {
    fontSize: 14,
    fontWeight: '700',
  },
  sectionContent: {
    padding: spacing.lg,
  },
  
  // Comision rows
  comisionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
  },
  comisionRowBorder: {
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  comisionInfo: {
    flex: 1,
  },
  comisionLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.textDark,
    marginBottom: 2,
  },
  comisionDetail: {
    fontSize: 12,
    color: colors.textMedium,
  },
  comisionAmount: {
    fontSize: 14,
    fontWeight: '700',
    color: colors.success,
  },
  deduccionAmount: {
    color: colors.error,
  },
  
  // Links
  viewAllLink: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: spacing.md,
    marginTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  viewAllText: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.primary,
  },
  addDeduccionLink: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    paddingTop: spacing.md,
    marginTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  addDeduccionText: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.primary,
  },
  
  // Empty state
  emptyState: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    paddingVertical: spacing.md,
  },
  emptyText: {
    fontSize: 13,
    color: colors.success,
  },
  
  // Historial
  historialRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  historialPeriodo: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.textDark,
  },
  historialFecha: {
    fontSize: 12,
    color: colors.textMedium,
    marginTop: 2,
  },
  historialRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  historialMonto: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textDark,
  },
  
  // Modal
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  modalContent: {
    backgroundColor: colors.white,
    borderRadius: radius.xl,
    padding: spacing['3xl'],
    width: '100%',
    maxWidth: 340,
    alignItems: 'center',
  },
  modalAvatar: {
    width: 72,
    height: 72,
    borderRadius: 36,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  modalAvatarText: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.white,
  },
  modalName: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.textDark,
    marginBottom: spacing.sm,
  },
  modalAmount: {
    fontSize: 32,
    fontWeight: '700',
    color: colors.primary,
    marginBottom: spacing.sm,
  },
  modalPeriodo: {
    fontSize: 13,
    color: colors.textMedium,
    marginBottom: spacing['2xl'],
  },
  methodsContainer: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing['2xl'],
  },
  methodButton: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.lg,
    borderRadius: radius.md,
    borderWidth: 2,
    borderColor: colors.border,
    gap: spacing.sm,
  },
  methodSelected: {
    borderColor: colors.primary,
    backgroundColor: colors.primaryBg,
  },
  methodText: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.textMedium,
  },
  methodTextSelected: {
    color: colors.primary,
  },
  confirmButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing['2xl'],
    borderRadius: radius.md,
    width: '100%',
    gap: spacing.sm,
  },
  confirmButtonDisabled: {
    backgroundColor: colors.textMedium,
    opacity: 0.5,
  },
  confirmButtonText: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.white,
  },
  cancelButton: {
    paddingVertical: spacing.md,
    marginTop: spacing.md,
  },
  cancelButtonText: {
    fontSize: 14,
    color: colors.textMedium,
    fontWeight: '500',
  },
  
  // Success state
  successContainer: {
    alignItems: 'center',
    paddingVertical: spacing['2xl'],
  },
  successIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.success,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  successTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.textDark,
    marginBottom: spacing.sm,
  },
  successSubtitle: {
    fontSize: 14,
    color: colors.textMedium,
  },
});
