/**
 * API — Settlements (Liquidaciones)
 *
 * Claudy ✨ — 2026-02-27
 * Conecta el frontend con el módulo de liquidaciones de FastAPI.
 * El backend devuelve datos directamente (sin wrapper ApiResponse).
 */

import api from './client';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface EmployeeBasic {
  employee_id: number;
  employee_role_id: number;
  code: string;
  full_name: string;
}

export interface CommissionDetail {
  count: number;
  amount_collected: number;
  percentage?: number;
  commission: number;
}

export interface CommissionBreakdown {
  regular: CommissionDetail;
  cash: CommissionDetail;
  delivery: CommissionDetail;
  total: number;
}

export interface DeductionItem {
  id?: number;
  type: 'fuel' | 'loan' | 'shortage' | 'other' | string;
  concept: string;
  description?: string;
  amount: number;
  loan_id?: number;
}

export interface DeductionBreakdown {
  items: DeductionItem[];
  total: number;
}

export interface PeriodInfo {
  start: string;
  end: string;
  label: string;
}

export interface SettlementPreview {
  employee: EmployeeBasic;
  period: PeriodInfo;
  goal_amount: number;
  total_collected: number;
  goal_percentage: number;
  commissions: CommissionBreakdown;
  deductions: DeductionBreakdown;
  net_amount: number;
  has_alerts: boolean;
  alerts: string[];
}

export interface SettlementHistoryItem {
  id: number;
  period_start: string;
  period_end: string;
  period_label: string;
  net_amount: number;
  amount_paid: number;
  status: string;
  paid_at?: string;
}

export interface SettlementHistoryResponse {
  employee: EmployeeBasic;
  items: SettlementHistoryItem[];
  total_paid: number;
}

export type PaymentMethod = 'cash' | 'transfer';

export interface SettlementCreate {
  employee_role_id: number;
  period_start: string;
  period_end: string;
  payment_method: PaymentMethod;
  amount?: number;
  notes?: string;
}

export interface SettlementBatchCreate {
  employee_role_ids: number[];
  period_start: string;
  period_end: string;
  payment_method: PaymentMethod;
  notes?: string;
}

export interface ManualDeductionCreate {
  settlement_id: number;
  type: string;
  concept: string;
  amount: number;
  notes?: string;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Convierte el método de pago del modal al formato del API */
export function toApiMethod(method: string): PaymentMethod {
  return method === 'transferencia' ? 'transfer' : 'cash';
}

// ── API Functions ─────────────────────────────────────────────────────────────

/**
 * GET /settlements/preview
 * Previews de TODOS los cobradores activos para el período.
 */
export async function getAllPreviews(
  period_start: string,
  period_end: string,
): Promise<SettlementPreview[]> {
  const { data } = await api.get<SettlementPreview[]>('/settlements/preview', {
    params: { period_start, period_end },
  });
  return data;
}

/**
 * GET /settlements/preview/{employee_role_id}
 * Preview individual de un cobrador.
 */
export async function getPreview(
  employee_role_id: number,
  period_start: string,
  period_end: string,
): Promise<SettlementPreview> {
  const { data } = await api.get<SettlementPreview>(
    `/settlements/preview/${employee_role_id}`,
    { params: { period_start, period_end } },
  );
  return data;
}

/**
 * GET /settlements/history/{employee_role_id}
 * Historial de liquidaciones de un cobrador.
 */
export async function getSettlementHistory(
  employee_role_id: number,
  limit = 10,
): Promise<SettlementHistoryResponse> {
  const { data } = await api.get<SettlementHistoryResponse>(
    `/settlements/history/${employee_role_id}`,
    { params: { limit } },
  );
  return data;
}

/**
 * POST /settlements/
 * Registra y paga la liquidación de un cobrador.
 */
export async function createSettlement(payload: SettlementCreate): Promise<any> {
  const { data } = await api.post('/settlements/', payload);
  return data;
}

/**
 * POST /settlements/batch
 * Registra y paga liquidaciones masivas ("Pagar todos los listos").
 */
export async function createBatchSettlement(payload: SettlementBatchCreate): Promise<any> {
  const { data } = await api.post('/settlements/batch', payload);
  return data;
}

/**
 * POST /settlements/deductions
 * Agrega una deducción manual a una liquidación pendiente.
 * Nota: requiere settlement_id — la liquidación debe existir primero.
 */
export async function addManualDeduction(payload: ManualDeductionCreate): Promise<any> {
  const { data } = await api.post('/settlements/deductions', payload);
  return data;
}
